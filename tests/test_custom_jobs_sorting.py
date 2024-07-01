import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
 
from oar.kao.kamelot import schedule_cycle
from oar.kao.platform import Platform
from oar.lib.database import ephemeral_session
from oar.lib.job_handling import insert_job
from oar.lib.models import GanttJobsPrediction, Resource

@pytest.fixture(scope="function", autouse=True)
def db(request, setup_config):
    _, engine = setup_config
    session_factory = sessionmaker(bind=engine)
    scoped = scoped_session(session_factory)
    
    with ephemeral_session(scoped, engine, bind=engine) as session:
        for i in range(5):
            Resource.create(session, network_address="localhost")
        yield session

@pytest.fixture(scope="module", autouse=True)
def oar_conf(request, setup_config):
    config, _ = setup_config
    config["JOB_PRIORITY"] = "CUSTOM"
    
    yield config
 
    @request.addfinalizer
    def remove_job_sorting():
        config["JOB_PRIORITY"] = "FIFO"
        config["CUSTOM_JOB_SORTING"] = ""
        config["CUSTOM_JOB_SORTING_CONFIG"] = ""


def test_db_job_sorting_simple_priority_no_waiting_time(db, oar_conf):
    config = oar_conf
    config["CUSTOM_JOB_SORTING"] = "simple_priority"

    plt = Platform()
    now = plt.get_time()

    # add some job with priority
    for i in range(10):
        priority = str(float(i) / 10.0)
        insert_job(
            db,
            res=[(60, [("resource_id=4", "")])],
            submission_time=now,
            types=["priority=" + priority],
        )

    schedule_cycle(db, config, plt, plt.get_time() )

    req = db.query(GanttJobsPrediction).order_by(GanttJobsPrediction.start_time).all()
    
    flag = True

    print(req)
    for r in req:
        print(r.moldable_id, r.start_time)

    prev_id = req[0].moldable_id
    for i, r in enumerate(req):
        if i != 0:
            print(r.moldable_id, prev_id)
            if r.moldable_id > prev_id:
                flag = False
                break
        prev_id = r.moldable_id

    assert flag

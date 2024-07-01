# coding: utf-8
import pytest

from sqlalchemy.orm import scoped_session, sessionmaker

import oar.lib.tools  # for monkeypatching
from oar.kao.meta_sched import meta_schedule

from oar.lib.database import ephemeral_session
from oar.lib.job_handling import insert_job
from oar.lib.models import Job, Queue, Resource, GanttJobsPrediction


@pytest.fixture(scope="function", autouse=True)
def db(request, setup_config):
    _, engine = setup_config
    session_factory = sessionmaker(bind=engine)
    scoped = scoped_session(session_factory)
    
    with ephemeral_session(scoped, engine, bind=engine) as session:
        Queue.create(session, name="default", priority=3, scheduler_policy="kamelot", state="Active")
        for i in range(5):
            Resource.create(session, network_address="localhost")
        yield session


@pytest.fixture(scope="function", autouse=True)
def monkeypatch_tools(request, monkeypatch):
    monkeypatch.setattr(oar.lib.tools, "create_almighty_socket", lambda x,y: None)
    monkeypatch.setattr(oar.lib.tools, "notify_almighty", lambda x: True)
    monkeypatch.setattr(oar.lib.tools, "notify_bipbip_commander", lambda x: True)
    monkeypatch.setattr(
        oar.lib.tools, "notify_tcp_socket", lambda addr, port, msg: len(msg)
    )
    monkeypatch.setattr(
        oar.lib.tools, "notify_user", lambda job, state, msg: len(state + msg)
    )


@pytest.fixture(scope="module", autouse=True)
def oar_conf(request, setup_config):
    config, _ = setup_config
    yield config
    
    @request.addfinalizer
    def remove_job_sorting():
        config["EXTRA_METASCHED"] = "default"


def test_db_extra_metasched_1(db, oar_conf, monkeypatch_tools):
    config = oar_conf
    config["EXTRA_METASCHED"] = "foo"

    insert_job(db, res=[(60, [("resource_id=1", "")])], properties="deploy='YES'")
    insert_job(db, res=[(60, [("resource_id=1", "")])], properties="deploy='FOO'")
    insert_job(db, res=[(60, [("resource_id=1", "")])], properties="")

    for job in db.query(Job).all():
        print("job state:", job.state, job.id)

    meta_schedule(db, config)

    for i in  db.query(GanttJobsPrediction).all():
        print("moldable_id: ", i.moldable_id, " start_time: ", i.start_time)

    states = [job.state for job in db.query(Job).order_by(Job.id).all()]
    print(states)
    assert states == ["toLaunch", "Waiting", "toLaunch"]

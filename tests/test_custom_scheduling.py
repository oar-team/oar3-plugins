# coding: utf-8
from procset import ProcSet

from oar.kao.scheduling import schedule_id_jobs_ct, set_slots_with_prev_scheduled_jobs
from oar.kao.slot import Slot, SlotSet
from oar.lib import config
from oar.lib.job_handling import JobPseudo
from oar.lib.plugins import find_plugin_function

config["LOG_FILE"] = ":stderr:"

ASSIGN_ENTRY_POINTS = "oar.assign_func"
FIND_ENTRY_POINTS = "oar.find_func"


def set_assign_func(job, name, args=[], kwargs={}):

    job.assign = True
    job.assign_nargs = args
    job.assign_kwargs = kwargs

    job.assign_func = find_plugin_function(ASSIGN_ENTRY_POINTS, name)


def set_find_func(job, name, args=[], kwargs={}):

    job.find = True
    job.find_args = args
    job.find_kwargs = kwargs

    job.find_func = find_plugin_function(FIND_ENTRY_POINTS, name)


def test_find_even_odd():

    # Setting up the resources of the platform
    res = ProcSet(*[(1, 32)])
    ss = SlotSet(Slot(1, 0, 0, res, 0, 1000))
    all_ss = {"default": ss}

    # Creating a resources hierarchy
    hy = {}
    hy["resource_id"] = [ProcSet(i) for i in range(1, 33)]

    # We create two jobs
    j1 = JobPseudo(
        id=1,
        mld_res_rqts=[(1, 60, [([("resource_id", 16)], ProcSet(*[(1, 32)]))])],
    )

    j2 = JobPseudo(
        id=2,
        mld_res_rqts=[(1, 60, [([("resource_id", 16)], ProcSet(*[(1, 32)]))])],
    )

    # and we set the find function
    set_find_func(j1, "find_even_or_odd", args=["even"])
    set_find_func(j2, "find_even_or_odd", args=["odd"])

    # Now we start a scheduling loop
    schedule_id_jobs_ct(all_ss, {1: j1, 2: j2}, hy, [1, 2], 20)

    # Now we can tests the job allocations
    assert all([resource_id % 2 == 0 for resource_id in j1.res_set])
    assert all([resource_id % 2 != 0 for resource_id in j2.res_set])


def compare_slots_val_ref(slots, v):
    sid = 1
    i = 0
    while True:
        slot = slots[sid]
        (b, e, itvs) = v[i]
        if (slot.b != b) or (slot.e != e) or not (slot.itvs == itvs):
            return False
        sid = slot.next
        if sid == 0:
            break
        i += 1
    return True


def test_assign_default():

    v = [(0, 59, ProcSet(*[(17, 32)])), (60, 100, ProcSet(*[(1, 32)]))]

    res = ProcSet(*[(1, 32)])
    ss = SlotSet(Slot(1, 0, 0, res, 0, 100))
    all_ss = {"default": ss}
    hy = {"node": [ProcSet(*x) for x in [[(1, 8)], [(9, 16)], [(17, 24)], [(25, 32)]]]}

    j1 = JobPseudo(
        id=1,
        types={},
        deps=[],
        key_cache={},
        mld_res_rqts=[(1, 60, [([("node", 2)], res)])],
    )

    set_assign_func(j1, "default")

    schedule_id_jobs_ct(all_ss, {1: j1}, hy, [1], 20)

    assert compare_slots_val_ref(ss.slots, v) is True


def test_find_default():

    v = [(0, 59, ProcSet(*[(17, 32)])), (60, 100, ProcSet(*[(1, 32)]))]

    res = ProcSet(*[(1, 32)])
    ss = SlotSet(Slot(1, 0, 0, res, 0, 100))
    all_ss = {"default": ss}
    hy = {"node": [ProcSet(*x) for x in [[(1, 8)], [(9, 16)], [(17, 24)], [(25, 32)]]]}

    j1 = JobPseudo(
        id=1,
        types={},
        deps=[],
        key_cache={},
        mld_res_rqts=[(1, 60, [([("node", 2)], res)])],
    )

    set_find_func(j1, "default")

    schedule_id_jobs_ct(all_ss, {1: j1}, hy, [1], 20)

    assert compare_slots_val_ref(ss.slots, v) is True

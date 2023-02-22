# coding: utf-8
from procset import ProcInt, ProcSet

import oar.kao.scheduling
from oar.lib import config, get_logger
from oar.lib.hierarchy import extract_n_scattered_block_itv
from oar.kao.scheduling_basic import find_first_suitable_contiguous_slots 

try:
    import zerorpc
except ImportError:
    zerorpc = None

logger = get_logger("oar.custom_scheduling")


def find_default(itvs_avail, hy_res_rqts, hy, beginning, *find_args, **find_kwargs):
    """Simple wrap function to default function for test purpose"""
    logger.debug(f"find_default function from plugin {find_args} {find_kwargs}")
    return oar.kao.scheduling.find_resource_hierarchies_job(itvs_avail, hy_res_rqts, hy)


def assign_default(slots_set, job, hy, min_start_time, *assign_args, **assign_kwargs):
    """Simple wrap function to default function for test purpose"""
    logger.debug(f"assign_default function from plugin {assign_args} {assign_kwargs}")
    return oar.kao.scheduling.assign_resources_mld_job_split_slots(
        slots_set, job, hy, min_start_time
    )


def find_even_or_odd(itvs_avail, hy_res_rqts, hy, beginning, *assign_args):
    if assign_args[0] == 'odd':
        itvs_avail = ProcSet(*[res_id for res_id in itvs_avail if res_id % 2 != 0])
    else:
        itvs_avail = ProcSet(*[res_id for res_id in itvs_avail if res_id % 2 == 0])

    return oar.kao.scheduling.find_resource_hierarchies_job(itvs_avail, hy_res_rqts, hy)


def assign_start_every_minute(slots_set, job, hy, *assign_args, **assign_kwarg):
    """
    """

    prev_t_finish = 2**32 - 1  # large enough
    prev_res_set = ProcSet()
    prev_res_rqt = ProcSet()

    slots = slots_set.slots
    prev_start_time = slots[1].b

    for res_rqt in job.mld_res_rqts:
        (mld_id, walltime, hy_res_rqts) = res_rqt
        (res_set, sid_left, sid_right) = find_first_suitable_contiguous_slots(
            slots_set, job, res_rqt, hy
        )
        # print("after find fisrt suitable")
        t_finish = slots[sid_left].b + walltime
        if t_finish < prev_t_finish:
            prev_start_time = slots[sid_left].b
            prev_t_finish = t_finish
            prev_res_set = res_set
            prev_res_rqt = res_rqt
            prev_sid_left = sid_left
            prev_sid_right = sid_right

    (mld_id, walltime, hy_res_rqts) = prev_res_rqt
    job.moldable_id = mld_id
    job.res_set = prev_res_set
    job.start_time = prev_start_time + (60 - (prev_start_time % 60))
    job.walltime = walltime

    slots_set.split_slots(prev_sid_left, prev_sid_right, job)
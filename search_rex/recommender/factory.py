from rec_service import RecommenderService
from data_model import ActionDataModelWrapper


def create_rec_service(
        data_model, action_type, include_internal_records,
        query_based_recsys_factory, record_based_recsys_factory):

    model_wrapper = ActionDataModelWrapper(
        data_model, action_type=action_type,
        include_internal_records=include_internal_records)

    q_based_recsys = query_based_recsys_factory(model_wrapper)
    r_based_recsys = record_based_recsys_factory(model_wrapper)

    return RecommenderService(
        query_based_recsys=q_based_recsys,
        record_based_recsys=r_based_recsys)

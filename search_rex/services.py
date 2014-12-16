from recommender.factory import create_rec_system
from models import ActionType


internal_view_action_recommender = create_rec_system(
    action_type=ActionType.view, include_internal_records=True,
    k_shingles=3, sim_threshold=0.2)
internal_copy_action_recommender = create_rec_system(
    action_type=ActionType.view, include_internal_records=True,
    k_shingles=3, sim_threshold=0.2)
external_view_action_recommender = create_rec_system(
    action_type=ActionType.view, include_internal_records=False,
    k_shingles=3, sim_threshold=0.2)
external_copy_action_recommender = create_rec_system(
    action_type=ActionType.view, include_internal_records=False,
    k_shingles=3, sim_threshold=0.2)

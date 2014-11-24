from recommender.factory import create_rec_system


rec_service = create_rec_system(k_shingles=3, sim_threshold=0.2)

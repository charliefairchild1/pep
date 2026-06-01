"""FastAPI app for PEP. `uv run pep serve` boots this."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from pep import __version__
from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import get_llm_client
from pep.routes import chat, debug
from pep.routes.axona import router as axona_router
from pep.routes.axona_bridge import router as axona_bridge_router
from pep.routes.axona_pep_insights import router as axona_pep_insights_router
from pep.routes.atria import router as atria_router
from pep.routes.atria_bridge import router as atria_bridge_router
from pep.routes.lingora import router as lingora_router
from pep.routes.lingora_bridge import router as lingora_bridge_router
from pep.routes.landing import router as landing_router
from pep.routes.everything import router as everything_router
from pep.routes.axona_brain import router as axona_brain_router
from pep.routes.axona_seizure import router as axona_seizure_router
from pep.routes.axona_seeming import router as axona_seeming_router
from pep.routes.axona_origin import router as axona_origin_router
from pep.routes.axona_mind import router as axona_mind_router
from pep.routes.robot import router as robot_router
from pep.routes.village import router as village_router
from pep.routes.encounter import router as encounter_router
from pep.routes.passage import router as passage_router
from pep.routes.cooking_app import router as cooking_app_router
from pep.routes.plan import router as plan_router
from pep.routes.domain_apps import router as domain_apps_router
from pep.routes.apps_book import router as apps_book_router
from pep.routes.ai_self_explorable import router as ai_self_router
from pep.routes.moral_luck_explorable import router as moral_luck_router
from pep.routes.sync_explorable import router as sync_router
from pep.routes.the_return import router as the_return_router
from pep.routes.pep_home import router as pep_home_router
from pep.routes.pto import router as pto_router
from pep.routes.product_pages import router as product_pages_router
from pep.routes.vectora_dogfood import router as vectora_dogfood_router
from pep.routes.vectora_playground import router as vectora_playground_router
from pep.routes.vectora_product_apis import router as vectora_product_apis_router
from pep.routes.atria_match_api import router as atria_match_api_router
from pep.routes.atria_products_api import router as atria_products_api_router
from pep.routes.axona_products_api import router as axona_products_api_router
from pep.routes.strata_products_api import router as strata_products_api_router
from pep.routes.lingora_prompt_api import router as lingora_prompt_api_router
from pep.routes.lingora_prompt_playground import router as lingora_prompt_playground_router
from pep.routes.lingora_products_api import router as lingora_products_api_router
from pep.routes.strata import router as strata_router
from pep.routes.strata_bridge import router as strata_bridge_router
from pep.routes.vectora import router as vectora_router
from pep.routes.vectora_bridge import router as vectora_bridge_router
from pep.routes.koin import router as koin_router
from pep.routes.koin_v1 import router as koin_v1_router
from pep.routes.math_playground import router as math_router
from pep.routes.math_globe import router as math_globe_router
from pep.routes.math_language import router as math_language_router
from pep.routes.math_evolution_calculus import router as math_evolution_calculus_router
from pep.routes.calc_bc import router as calc_bc_router
from pep.routes.lemma_select import router as lemma_select_router
from pep.routes.lemma_science import router as lemma_science_router
from pep.routes.lemma_english import router as lemma_english_router
from pep.routes.lemma_history import router as lemma_history_router
from pep.routes.lemma_languages import router as lemma_languages_router
from pep.routes.lemma_arts import router as lemma_arts_router
from pep.routes.lemma_cs import router as lemma_cs_router
from pep.routes.lemma_testprep import router as lemma_testprep_router
from pep.routes.lemma_engineering import router as lemma_engineering_router
from pep.routes.lemma_sales import router as lemma_sales_router
from pep.routes.apex import router as apex_router
from pep.routes.lemma_backend import router as lemma_backend_router
from pep.routes.lemma_canvas import router as lemma_canvas_router
from pep.routes.lemma_accounts import router as lemma_accounts_router
from pep.routes.pep_book_full import router as pep_book_full_router
from pep.routes.pep_book_engine import router as pep_book_engine_router
from pep.routes.substrate_landing import router as substrate_landing_router
from pep.routes.substrate_math import router as substrate_math_router
from pep.routes.substrate_atlas import router as substrate_atlas_router
from pep.routes.substrate_practice import router as substrate_practice_router
from pep.routes.substrate_video import router as substrate_video_router
from pep.routes.substrate_threads import router as substrate_threads_router
from pep.routes.substrate_cards import router as substrate_cards_router
from pep.routes.substrate_audio import router as substrate_audio_router
from pep.routes.substrate_sandbox import router as substrate_sandbox_router
from pep.routes.substrate_explainers import router as substrate_explainers_router
from pep.routes.substrate_convictions import router as substrate_convictions_router
from pep.routes.substrate_quotes import router as substrate_quotes_router
from pep.routes.substrate_prompts import router as substrate_prompts_router
from pep.routes.substrate_book import router as substrate_book_router
from pep.routes.substrate_core import router as substrate_core_router
from pep.routes.substrate_personas import router as substrate_personas_router
from pep.routes.pep_app_books import router as pep_app_books_router
from pep.routes.recipes import router as recipes_router
from pep.routes.math_life import router as math_life_router
from pep.routes.math_voronoi import router as math_voronoi_router
from pep.routes.math_epidemic import router as math_epidemic_router
from pep.routes.math_predictor import router as math_predictor_router
from pep.routes.math_matcher import router as math_matcher_router
from pep.routes.math_spreading import router as math_spreading_router
from pep.routes.math_haze import router as math_haze_router
from pep.routes.math_modulation import router as math_modulation_router
from pep.routes.math_novelty import router as math_novelty_router
from pep.routes.math_attractor import router as math_attractor_router
from pep.routes.math_evolution import router as math_evolution_router
from pep.routes.math_cycles import router as math_cycles_router
from pep.routes.math_bayes import router as math_bayes_router
from pep.routes.math_game import router as math_game_router
from pep.routes.math_entropy import router as math_entropy_router
from pep.routes.math_diffusion import router as math_diffusion_router
from pep.routes.math_fourier import router as math_fourier_router
from pep.routes.math_percolation import router as math_percolation_router
from pep.routes.math_kuramoto import router as math_kuramoto_router
from pep.routes.math_galton import router as math_galton_router
from pep.routes.math_gradient import router as math_gradient_router
from pep.routes.math_markov import router as math_markov_router
from pep.routes.math_pendulum import router as math_pendulum_router
from pep.routes.math_reaction import router as math_reaction_router
from pep.routes.math_mcmc import router as math_mcmc_router
from pep.routes.math_annealing import router as math_annealing_router
from pep.routes.math_boids import router as math_boids_router
from pep.routes.math_ising import router as math_ising_router
from pep.routes.math_wolfram import router as math_wolfram_router
from pep.routes.math_pca import router as math_pca_router
from pep.routes.math_spatial_pd import router as math_spatial_pd_router
from pep.routes.math_waves import router as math_waves_router
from pep.routes.math_direction_cycles import router as math_direction_cycles_router
from pep.routes.math_nav import router as math_nav_router
from pep.routes.math_bridge import router as math_bridge_router
from pep.routes.math_network import router as math_network_router
from pep.routes.math_gp import router as math_gp_router
from pep.routes.math_neural import router as math_neural_router
from pep.routes.pep_narrative import router as pep_narrative_router
from pep.routes.app_labs import router as app_labs_router
from pep.routes.math_sandpile import router as math_sandpile_router
from pep.routes.pep_quickstart import router as pep_quickstart_router
from pep.routes.math_3body import router as math_3body_router
from pep.routes.math_stochastic_resonance import router as math_sr_router
from pep.routes.math_schelling import router as math_schelling_router
from pep.routes.math_wealth import router as math_wealth_router
from pep.routes.math_qlearning import router as math_qlearning_router
from pep.routes.math_discover import router as math_discover_router
from pep.routes.math_info_bottleneck import router as math_ib_router
from pep.routes.math_active_inference import router as math_ai_router
from pep.routes.math_voting import router as math_voting_router
from pep.routes.math_auction import router as math_auction_router
from pep.routes.math_bifurcation import router as math_bifurcation_router
from pep.routes.math_pendulum_cloud import router as math_pcloud_router
from pep.routes.biology import router as biology_router
from pep.routes.pep_branching import router as pep_branching_router
from pep.routes.pep_datascience import router as pep_datascience_router
from pep.routes.pep_applications import router as pep_applications_router
from pep.routes.axona_cognition import router as axona_cognition_router
from pep.routes.pep_ideas import router as pep_ideas_router
from pep.routes.pep_teams import router as pep_teams_router
from pep.routes.pep_personal import router as pep_personal_router
from pep.routes.pep_climate import router as pep_climate_router
from pep.routes.pep_medicine import router as pep_medicine_router
from pep.routes.pep_education import router as pep_education_router
from pep.routes.pep_relationships import router as pep_relationships_router
from pep.routes.pep_timescales import router as pep_timescales_router
from pep.routes.pep_law import router as pep_law_router
from pep.routes.pep_cities import router as pep_cities_router
from pep.routes.pep_why import router as pep_why_router
from pep.routes.pep_glossary import router as pep_glossary_router
from pep.routes.pep_journalism import router as pep_journalism_router
from pep.routes.pep_agriculture import router as pep_agriculture_router
from pep.routes.pep_explore import router as pep_explore_router
from pep.routes.pep_finance import router as pep_finance_router
from pep.routes.pep_sports import router as pep_sports_router
from pep.routes.pep_art import router as pep_art_router
from pep.routes.pep_music import router as pep_music_router
from pep.routes.pep_therapy import router as pep_therapy_router
from pep.routes.pep_ecology import router as pep_ecology_router
from pep.routes.pep_diplomacy import router as pep_diplomacy_router
from pep.routes.pep_religion import router as pep_religion_router
from pep.routes.pep_cooking import router as pep_cooking_router
from pep.routes.pep_games import router as pep_games_router
from pep.routes.pep_start import router as pep_start_router
from pep.routes.pep_cards import router as pep_cards_router
from pep.routes.pep_parenting import router as pep_parenting_router
from pep.routes.pep_conflict import router as pep_conflict_router
from pep.routes.pep_career import router as pep_career_router
from pep.routes.pep_aging import router as pep_aging_router
from pep.routes.pep_leadership import router as pep_leadership_router
from pep.routes.pep_sleep import router as pep_sleep_router
from pep.routes.pep_decisions import router as pep_decisions_router
from pep.routes.pep_communication import router as pep_communication_router
from pep.routes.pep_innovation import router as pep_innovation_router
from pep.routes.pep_body import router as pep_body_router
from pep.routes.pep_math_language import router as pep_math_language_router
from pep.routes.pep_chemistry import router as pep_chemistry_router
from pep.routes.pep_animation import router as pep_animation_router
from pep.routes.pep_robotics import router as pep_robotics_router
from pep.routes.pep_book import router as pep_book_router
from pep.routes.pep_book_chapters import router as pep_book_chapters_router
from pep.routes.pep_consciousness import router as pep_consciousness_router
from pep.routes.pep_language_acq import router as pep_language_acq_router
from pep.routes.pep_software import router as pep_software_router
from pep.routes.pep_trust import router as pep_trust_router
from pep.routes.pep_storytelling import router as pep_storytelling_router
from pep.routes.pep_curiosity import router as pep_curiosity_router
from pep.routes.pep_forgiveness import router as pep_forgiveness_router
from pep.routes.pep_regret import router as pep_regret_router
from pep.routes.pep_logic import router as pep_logic_router
from pep.routes.pep_attention import router as pep_attention_router
from pep.routes.pep_money import router as pep_money_router
from pep.routes.pep_identity import router as pep_identity_router
from pep.routes.pep_loneliness import router as pep_loneliness_router
from pep.routes.pep_play import router as pep_play_router
from pep.routes.pep_values import router as pep_values_router
from pep.routes.pep_honesty import router as pep_honesty_router
from pep.routes.pep_boredom import router as pep_boredom_router
from pep.routes.pep_forecasting import router as pep_forecasting_router
from pep.routes.pep_responsibility import router as pep_responsibility_router
from pep.routes.pep_community import router as pep_community_router
from pep.routes.pep_courage import router as pep_courage_router
from pep.routes.pep_exercise import router as pep_exercise_router
from pep.routes.pep_charity import router as pep_charity_router
from pep.routes.pep_protest import router as pep_protest_router
from pep.routes.pep_migration import router as pep_migration_router
from pep.routes.forecast import router as forecast_router
from pep.routes.node_dating import router as node_dating_router
from pep.routes.scene import router as scene_router
from pep.routes.openai_compat import router as openai_router
from pep.routes.ui import router as ui_router


def _resolve_db_path() -> str:
    custom = os.environ.get("PEP_DB_PATH")
    if custom:
        return custom
    return str(Path("data") / "pep.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    app.state.store = MemoryStore(_resolve_db_path())
    app.state.embedder = Embedder()
    app.state.llm = get_llm_client()
    # Thread-safe stop flag for the dialogue runner. Only one dialogue runs
    # at a time, so a single Event is enough.
    app.state.dialogue_stop = threading.Event()
    yield
    app.state.store.close()


app = FastAPI(
    title="PEP — Predictive Encoding and Preparation",
    description=(
        "A predictive overlay that prepares an AI by activating likely-relevant "
        "memory, compressing the predictable, and highlighting useful novelty."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.include_router(chat.router)
app.include_router(debug.router)
app.include_router(openai_router)
app.include_router(math_router)
app.include_router(math_globe_router)
app.include_router(math_language_router)
app.include_router(math_evolution_calculus_router)
app.include_router(calc_bc_router)
app.include_router(lemma_select_router)
app.include_router(lemma_science_router)
app.include_router(lemma_english_router)
app.include_router(lemma_history_router)
app.include_router(lemma_languages_router)
app.include_router(lemma_arts_router)
app.include_router(lemma_cs_router)
app.include_router(lemma_testprep_router)
app.include_router(lemma_engineering_router)
app.include_router(lemma_sales_router)
app.include_router(apex_router)
app.include_router(lemma_backend_router)
app.include_router(lemma_canvas_router)
app.include_router(lemma_accounts_router)
app.include_router(pep_book_full_router)
app.include_router(pep_book_engine_router)
app.include_router(substrate_landing_router)
app.include_router(substrate_math_router)
app.include_router(substrate_atlas_router)
app.include_router(substrate_practice_router)
app.include_router(substrate_video_router)
app.include_router(substrate_threads_router)
app.include_router(substrate_cards_router)
app.include_router(substrate_audio_router)
app.include_router(substrate_sandbox_router)
app.include_router(substrate_explainers_router)
app.include_router(substrate_convictions_router)
app.include_router(substrate_quotes_router)
app.include_router(substrate_prompts_router)
app.include_router(substrate_book_router)
app.include_router(substrate_core_router)
app.include_router(substrate_personas_router)
app.include_router(pep_app_books_router)
app.include_router(recipes_router)
app.include_router(math_life_router)
app.include_router(math_voronoi_router)
app.include_router(math_epidemic_router)
app.include_router(math_predictor_router)
app.include_router(math_matcher_router)
app.include_router(math_spreading_router)
app.include_router(math_haze_router)
app.include_router(math_modulation_router)
app.include_router(math_novelty_router)
app.include_router(math_attractor_router)
app.include_router(math_evolution_router)
app.include_router(math_cycles_router)
app.include_router(math_bayes_router)
app.include_router(math_game_router)
app.include_router(math_entropy_router)
app.include_router(math_diffusion_router)
app.include_router(math_fourier_router)
app.include_router(math_percolation_router)
app.include_router(math_kuramoto_router)
app.include_router(math_galton_router)
app.include_router(math_gradient_router)
app.include_router(math_markov_router)
app.include_router(math_pendulum_router)
app.include_router(math_reaction_router)
app.include_router(math_mcmc_router)
app.include_router(math_annealing_router)
app.include_router(math_boids_router)
app.include_router(math_ising_router)
app.include_router(math_wolfram_router)
app.include_router(math_pca_router)
app.include_router(math_spatial_pd_router)
app.include_router(math_waves_router)
app.include_router(math_direction_cycles_router)
app.include_router(math_nav_router)
app.include_router(math_bridge_router)
app.include_router(math_network_router)
app.include_router(math_gp_router)
app.include_router(math_neural_router)
app.include_router(pep_narrative_router)
app.include_router(app_labs_router)
app.include_router(math_sandpile_router)
app.include_router(pep_quickstart_router)
app.include_router(math_3body_router)
app.include_router(math_sr_router)
app.include_router(math_schelling_router)
app.include_router(math_wealth_router)
app.include_router(math_qlearning_router)
app.include_router(math_discover_router)
app.include_router(math_ib_router)
app.include_router(math_ai_router)
app.include_router(math_voting_router)
app.include_router(math_auction_router)
app.include_router(math_bifurcation_router)
app.include_router(math_pcloud_router)
app.include_router(biology_router)
app.include_router(pep_branching_router)
app.include_router(pep_datascience_router)
app.include_router(pep_applications_router)
app.include_router(axona_cognition_router)
app.include_router(pep_ideas_router)
app.include_router(pep_teams_router)
app.include_router(pep_personal_router)
app.include_router(pep_climate_router)
app.include_router(pep_medicine_router)
app.include_router(pep_education_router)
app.include_router(pep_relationships_router)
app.include_router(pep_timescales_router)
app.include_router(pep_law_router)
app.include_router(pep_cities_router)
app.include_router(pep_why_router)
app.include_router(pep_glossary_router)
app.include_router(pep_journalism_router)
app.include_router(pep_agriculture_router)
app.include_router(pep_explore_router)
app.include_router(pep_finance_router)
app.include_router(pep_sports_router)
app.include_router(pep_art_router)
app.include_router(pep_music_router)
app.include_router(pep_therapy_router)
app.include_router(pep_ecology_router)
app.include_router(pep_diplomacy_router)
app.include_router(pep_religion_router)
app.include_router(pep_cooking_router)
app.include_router(pep_games_router)
app.include_router(pep_start_router)
app.include_router(pep_cards_router)
app.include_router(pep_parenting_router)
app.include_router(pep_conflict_router)
app.include_router(pep_career_router)
app.include_router(pep_aging_router)
app.include_router(pep_leadership_router)
app.include_router(pep_sleep_router)
app.include_router(pep_decisions_router)
app.include_router(pep_communication_router)
app.include_router(pep_innovation_router)
app.include_router(pep_body_router)
app.include_router(pep_math_language_router)
app.include_router(pep_chemistry_router)
app.include_router(pep_animation_router)
app.include_router(pep_robotics_router)
app.include_router(pep_book_router)
app.include_router(pep_book_chapters_router)
app.include_router(pep_consciousness_router)
app.include_router(pep_language_acq_router)
app.include_router(pep_software_router)
app.include_router(pep_trust_router)
app.include_router(pep_storytelling_router)
app.include_router(pep_curiosity_router)
app.include_router(pep_forgiveness_router)
app.include_router(pep_regret_router)
app.include_router(pep_logic_router)
app.include_router(pep_attention_router)
app.include_router(pep_money_router)
app.include_router(pep_identity_router)
app.include_router(pep_loneliness_router)
app.include_router(pep_play_router)
app.include_router(pep_values_router)
app.include_router(pep_honesty_router)
app.include_router(pep_boredom_router)
app.include_router(pep_forecasting_router)
app.include_router(pep_responsibility_router)
app.include_router(pep_community_router)
app.include_router(pep_courage_router)
app.include_router(pep_exercise_router)
app.include_router(pep_charity_router)
app.include_router(pep_protest_router)
app.include_router(pep_migration_router)
app.include_router(forecast_router)
app.include_router(node_dating_router)
app.include_router(scene_router)
app.include_router(axona_router)
app.include_router(axona_bridge_router)
app.include_router(axona_pep_insights_router)
app.include_router(lingora_router)
app.include_router(lingora_bridge_router)
app.include_router(atria_router)
app.include_router(atria_bridge_router)
app.include_router(landing_router)
app.include_router(everything_router)
app.include_router(axona_brain_router)
app.include_router(axona_seizure_router)
app.include_router(axona_seeming_router)
app.include_router(axona_origin_router)
app.include_router(axona_mind_router)
app.include_router(robot_router)
app.include_router(village_router)
app.include_router(encounter_router)
app.include_router(passage_router)
app.include_router(cooking_app_router)
app.include_router(plan_router)
app.include_router(domain_apps_router)
app.include_router(apps_book_router)
app.include_router(ai_self_router)
app.include_router(moral_luck_router)
app.include_router(sync_router)
app.include_router(the_return_router)
app.include_router(pep_home_router)
app.include_router(pto_router)
app.include_router(product_pages_router)
app.include_router(vectora_playground_router)
app.include_router(vectora_dogfood_router)
app.include_router(vectora_product_apis_router)
app.include_router(lingora_prompt_api_router)
app.include_router(lingora_prompt_playground_router)
app.include_router(lingora_products_api_router)
app.include_router(atria_match_api_router)
app.include_router(atria_products_api_router)
app.include_router(axona_products_api_router)
app.include_router(strata_products_api_router)
app.include_router(strata_router)
app.include_router(strata_bridge_router)
app.include_router(vectora_router)
app.include_router(vectora_bridge_router)
app.include_router(koin_router)
app.include_router(koin_v1_router)
app.include_router(ui_router)


# Root "/" is served by landing_router (the unified LAVAS landing page)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm": app.state.llm.name,
        "embeddings": "voyage" if app.state.embedder.using_real_embeddings else "pseudo",
    }

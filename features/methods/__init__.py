from features.display_tokens import DisplayTokensFrame
from features.methods.cosine_similarity import CosineSimilarityFrame
from features.methods.shap_values import ShapValuesFrame

FEATURE_FRAMES = {
    "display_tokens": DisplayTokensFrame,
    "cosine_similarity": CosineSimilarityFrame,
    "shap_values": ShapValuesFrame,
}

MODEL_UNIT = "UNIT"
MODEL_CLIP = "CLIP"

model_list = []


def get_models(model):
	i = 0
	model_size = len(model_list)
	models_retrieved = []
	while i < model_size:
		if models_retrieved[i].type == model:
			models_retrieved.append(models_retrieved[i])
		i += 1

	return models_retrieved


def register_model(model, model_type):
	model_list.append({"model": model, "type": model_type})
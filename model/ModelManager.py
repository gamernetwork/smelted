MODEL_UNIT = "UNIT"
MODEL_CLIP = "CLIP"

model_list = []

model_added_callbacks = []


def get_models(model):
	i = 0
	model_size = len(model_list)
	models_retrieved = []
	while i < model_size:
		if model_list[i]['model_type'] == model:
			models_retrieved.append(model_list[i])
		i += 1

	return models_retrieved


def register_model(model, model_type):
	model_list.append({"model": model, "model_type": model_type})
	notify_model_added(model_type)


def register_on_model_added_callback(callback, model_type):
	model_added_callbacks.append({'callback': callback, 'model_type': model_type})


def notify_model_added(model_type):
	for callback in model_added_callbacks:
		if model_type == callback['model_type']:
			callback['callback']()
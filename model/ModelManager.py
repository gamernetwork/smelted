MODEL_UNIT = "UNIT"
MODEL_CLIP = "CLIP"

model_list = []

model_added_callbacks = []

model_removed_callbacks = []

model_list_emptied_callbacks = []


def get_models(model):
	i = 0
	model_size = len(model_list)
	models_retrieved = []
	while i < model_size:
		if model_list[i]['model_type'] == model:
			models_retrieved.append(model_list[i]['model'])
		i += 1

	return models_retrieved


def register_model(model, model_type):
	model_list.append({"model": model, "model_type": model_type})
	notify_model_added(model_type, model)


def remove_model(model_to_remove, model_type):
	for model in model_list:
		if model['model'] == model_to_remove and model['model_type'] == model_type:
			model_list.remove(model)
			break
	notify_model_removed(model_type, model_to_remove)


def empty_model_list(model_type):
	for model in model_list:
		if model['model_type'] == model_type:
			model_list.remove(model)
	notify_model_list_emptied(model_type)


def register_on_model_added_callback(callback, model_type):
	model_added_callbacks.append({'callback': callback, 'model_type': model_type})


def register_on_model_removed_callback(callback, model_type):
	model_removed_callbacks.append({'callback': callback, 'model_type': model_type})


def register_on_model_list_emptied_callback(callback, model_type):
	model_list_emptied_callbacks.append({'callback': callback, 'model_type': model_type})


def notify_model_added(model_type, model):
	for callback in model_added_callbacks:
		if model_type == callback['model_type']:
			callback['callback'](model)


def notify_model_removed(model_type, model=None):
	for callback in model_removed_callbacks:
		if model_type == callback['model_type']:
			callback['callback'](model)


def notify_model_list_emptied(model_type):
	for callback in model_list_emptied_callbacks:
		if model_type == callback['model_type']:
			callback['callback']()
"""Load and validate complete non-secret run settings; values live in TOML."""

from pathlib import Path
import math
import tomllib

CONFIG_PATH = Path('configs/development.toml')
ATTEMPT_FIELDS = {
    'solver_image', 'guard_image', 'target_image', 'wall_seconds', 'max_tool_calls',
    'max_model_turns', 'command_seconds', 'max_command_bytes', 'max_output_bytes',
    'max_write_bytes', 'memory_mb', 'workspace_mb', 'pids', 'cpus',
}
MODEL_FIELDS = {
    'model', 'base_url', 'reasoning_effort', 'max_output_tokens', 'max_input_bytes',
    'request_seconds', 'input_usd_per_million', 'output_usd_per_million',
    'cached_input_usd_per_million',
}


def validate_settings(settings: dict) -> None:
    if not isinstance(settings, dict) or settings.keys() != ATTEMPT_FIELDS:
        raise ValueError('Attempt settings must contain exactly the documented keys')
    for name, value in settings.items():
        if name.endswith('_image'):
            if not isinstance(value, str) or not value or value.startswith('-'):
                raise ValueError(f'{name} must be an image reference')
        elif name in {'wall_seconds', 'command_seconds', 'cpus'}:
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        elif type(value) is not int or value <= 0:
            raise ValueError(f'{name} must be a positive integer')
    if settings['max_output_bytes'] > 65_536 or settings['max_write_bytes'] > 1_048_576:
        raise ValueError('Output/write limits exceed the worker protocol bounds')


def validate_model_settings(settings: dict) -> None:
    if not isinstance(settings, dict) or settings.keys() != MODEL_FIELDS | {'max_requests'}:
        raise ValueError('Model settings must contain exactly the documented keys')
    for name in ('model', 'base_url', 'reasoning_effort'):
        if not isinstance(settings[name], str) or not settings[name].strip():
            raise ValueError(f'{name} must be nonempty text')
    if not settings['base_url'].startswith('https://'):
        raise ValueError('Model credentials require an HTTPS gateway')
    for name in ('max_requests', 'max_output_tokens', 'max_input_bytes'):
        if type(settings[name]) is not int or settings[name] < (1 if name == 'max_output_tokens' else 0):
            raise ValueError(f'{name} must be a bounded integer')
    for name in ('request_seconds', 'input_usd_per_million', 'output_usd_per_million',
                 'cached_input_usd_per_million'):
        value = settings[name]
        if (type(value) not in (int, float) or not math.isfinite(value) or value < 0
                or (value == 0 and name != 'cached_input_usd_per_million')):
            raise ValueError(f'{name} must be finite and within its allowed range')
    if settings['cached_input_usd_per_million'] > settings['input_usd_per_million']:
        raise ValueError('Cached input cannot exceed the configured input price')


def load_experiment(path: Path = CONFIG_PATH) -> tuple[dict, dict]:
    """Read all values explicitly and share one model-call allowance."""
    with path.open('rb') as handle:
        values = tomllib.load(handle)
    if values.keys() != {'attempt', 'model'}:
        raise ValueError('Experiment settings require attempt and model tables')
    settings, model = values['attempt'], values['model']
    validate_settings(settings)
    if not isinstance(model, dict) or model.keys() != MODEL_FIELDS:
        raise ValueError('Model table must contain exactly the documented keys; max_requests is derived from max_model_turns')
    model = model | {'max_requests': settings['max_model_turns']}
    validate_model_settings(model)
    return settings, model


def load_settings(path: Path = CONFIG_PATH) -> dict:
    """Read only the attempt controls from the same complete experiment file."""
    return load_experiment(path)[0]

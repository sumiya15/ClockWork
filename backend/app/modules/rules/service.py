import json
from ...core.paths import PROJECT_ROOT
from ...engine.rules import RuleSet
from . import repository


def load_seed():
    return RuleSet.model_validate(json.loads((PROJECT_ROOT / 'config' / 'demo_rules.json').read_text(encoding='utf-8')))


def publish_seed(db, rule, session):
    existing = repository.get(db, rule.rule_id, rule.version, session)
    if existing:
        original = {k: v for k, v in existing.items() if k in RuleSet.model_fields}
        if RuleSet.model_validate(original) != rule:
            raise ValueError('Published rule version is immutable; create a new version')
    else:
        repository.insert(db, rule, session)


def published(db):
    return [RuleSet.model_validate({k: v for k, v in row.items() if k in RuleSet.model_fields})
            for row in repository.published(db)]

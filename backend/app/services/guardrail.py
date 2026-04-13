"""
Guardrail: reject questions that are clearly outside the DevOps domain.

Two layers:
  1. Fast local keyword check  – zero API cost, instant response
  2. System-prompt enforcement – model itself refuses off-topic follow-ups
"""
import re
from typing import Tuple

_OFF_TOPIC_PATTERNS = re.compile(
    r"\b("
    # food & cooking
    r"recipe|cook(ing)?|bake|baking|ingredient|cuisine|restaurant|chef|meal|dish|food|"
    # entertainment
    r"movie|film|series|netflix|tv show|anime|music|song|album|artist|celebrity|actor|actress|"
    # sports
    r"football|soccer|basketball|cricket|tennis|sport|match|score|goal|player|team|league|"
    # personal / lifestyle
    r"relationship|dating|love|marriage|divorce|fashion|style|makeup|fitness|workout|gym|yoga|diet|"
    r"weight loss|pregnancy|baby|parenting|astrology|horoscope|zodiac|"
    # finance / unrelated domains
    r"stock market|crypto(currency)?|bitcoin|forex|invest(ing|ment)?|real estate|"
    # trivia / general knowledge off-topic
    r"who (is|was) [a-z]+ [a-z]+|tell me a joke|joke|riddle|poem|story|"
    # explicit non-tech
    r"politics|religion|election|god|pray(er)?|spiritual"
    r")\b",
    re.IGNORECASE,
)

_DEVOPS_SIGNALS = re.compile(
    r"\b("
    r"kubernetes|k8s|pod|container|docker|helm|kubectl|namespace|deployment|"
    r"service|ingress|configmap|secret|pvc|node|cluster|"
    r"ci[/ ]?cd|pipeline|github action|gitlab|jenkins|argocd|flux|"
    r"terraform|ansible|pulumi|cloudformation|iac|infra(structure)?|"
    r"aws|gcp|azure|cloud|ec2|s3|eks|gke|aks|lambda|fargate|"
    r"prometheus|grafana|alert|metric|log|trace|observ(ability)?|"
    r"nginx|istio|envoy|service mesh|load.?balan|"
    r"crash|error|fail(ure|ing)?|debug|troubleshoot|"
    r"cpu|memory|oom|resource|limit|request|quota|"
    r"network|dns|tls|ssl|cert(ificate)?|firewall|vpc|subnet|"
    r"bash|shell|script|cron|systemd|linux|unix|"
    r"database|postgres|mysql|redis|mongodb|backup|restore|"
    r"secret|vault|rbac|policy|permission|iam|role|"
    r"scale|autoscal|replica|canary|blue.?green|rollout|rollback"
    r")\b",
    re.IGNORECASE,
)

_REFUSAL_RESPONSE = (
    "I'm a DevOps AI assistant and I can only help with topics such as "
    "Kubernetes, Docker, CI/CD pipelines, cloud infrastructure (AWS/GCP/Azure), "
    "Terraform, monitoring, incident troubleshooting, and related DevOps practices. "
    "Please ask a DevOps-related question."
)


def check(message: str) -> Tuple[bool, str]:
    """
    Returns (allowed, reason).
    allowed=True  → proceed to Bedrock
    allowed=False → return refusal to user
    """
    text = message.strip()

    has_devops = bool(_DEVOPS_SIGNALS.search(text))
    has_off_topic = bool(_OFF_TOPIC_PATTERNS.search(text))

    if has_devops:
        return True, ""

    if has_off_topic:
        return False, _REFUSAL_RESPONSE

    short = len(text.split()) <= 4
    if short:
        return True, ""

    return True, ""

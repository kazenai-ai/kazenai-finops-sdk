#!/usr/bin/env python3
"""Workspace-level audit: every repo must route LLM calls through the spine."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.getenv("KAZENAI_AUDIT_ROOT", Path(__file__).resolve().parents[1])).resolve()

SKIP_DIRS = {
    ".venv",
    ".venv-bootstrap",
    ".venv-bootstrap-test",
    ".venv-test",
    ".git",
    "__pycache__",
    "node_modules",
    "kazenbench",
    "cdk",
    "infra",
    ".pytest_cache",
    "site-packages",
    "build",
    "dist",
    ".next",
}

SKIP_FILES = {
    "kazenai-agent-builder/scripts/audit_llm_calls.py",
    "scripts/audit_llm_calls_all.py",
    "kazenai-finops-sdk/scripts/audit_llm_calls_all.py",
    "kazenai-agent-builder/scripts/split_phase6_tier2_orchestrator.py",
    "kazenai-agent-builder/kazenbench/fake_model.py",
    "kazenai-agent-builder/tests/test_router_litellm_lazy_import.py",
    "kazenai-agent-builder/providers/router_integration.py",
    "kazenai-agent-builder/orchestrator/utils.py",
    "kazenai-agent-builder/diagnostics/doctor.py",
    "kazenai-agent-builder/cli/agent_commands.py",
    "kazenai-agent-brain/backend/scripts/audit_brain_llm.py",
    "kazenai-agent-orchestrator/infra/lib/orchestration-stack.ts",
}

ALLOWED_FILES = {
    "kazenai-core/kazenai/spine/guard.py",
    "kazenai-core/kazenai/monitor.py",
    "kazenai-agent-builder/routing/tool_calls.py",
    "kazenai-agent-builder/routing/client.py",
    "kazenai-agent-builder/state/embedding_store.py",
    "kazenai-agent-brain/backend/llm_client.py",
    "kazenai-agent-brain/backend/llm_guard.py",
    "kazenai-brain-copilot/backend/agent/turn.py",
    "kazenai-brain-copilot/backend/feedback/entity_extractor.py",
    "kazenai-brain-copilot/backend/feedback/intent_classifier.py",
    "kazenai-agent-growthops/backend/agents/base.py",
    "kazenai-agent-platform/backend/learning/run_ingestor.py",
    "kazenai-agent-orchestrator/backend/src/llm-adapter.ts",
}

PY_PATTERNS = (
    re.compile(r"\blitellm\.completion\s*\("),
    re.compile(r"\blitellm\.acompletion\s*\("),
    re.compile(r"\blitellm\.embedding\s*\("),
    re.compile(r"\bllm_complete\s*\("),
    re.compile(r"\.messages\.create\s*\("),
    re.compile(r"chat\.completions\.create\s*\("),
)

TS_PATTERNS = (
    re.compile(r"\bConverseCommand\s*\("),
    re.compile(r"@anthropic-ai/sdk"),
    re.compile(r"client-bedrock-runtime"),
)

GUARD_MARKERS = (
    "guarded_llm_call",
    "aguarded_llm_call",
    "guarded_embedding_call",
    "apply_pre_call_guards",
    "guard_before_llm_call",
    "call_model_with_retry",
    "call_model(",
    "call_model_with_tools",
    "call_model_explicit",
    "stream_model",
    "brain_llm_call",
    "runChatCompletion",
    "checkFinOpsBudget",
    "from kazenai.spine",
    "kazenai.spine.guard",
    "from kazenai_finops import monitor",
    "kazenai_finops import monitor",
)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _should_skip(path: Path) -> bool:
    rel = _rel(path)
    if rel in SKIP_FILES or rel in ALLOWED_FILES:
        return True
    if "/tests/" in f"/{rel}/" or rel.startswith("tests/"):
        return True
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    return False


def _is_actionable_py(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if stripped.startswith(('"""', "'''")):
        return False
    return any(p.search(line) for p in PY_PATTERNS)


def _is_actionable_ts(line: str, *, rel: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("//"):
        return False
    if "llm-adapter.ts" in rel:
        return False
    if "chat/completions" in line and "chatCompletionsUrl" in line:
        return False
    return any(p.search(line) for p in TS_PATTERNS)


def audit_repo(repo: Path) -> list[tuple[str, int, str]]:
    violations: list[tuple[str, int, str]] = []

    for path in sorted(repo.rglob("*.py")):
        if _should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        actionable = [
            (i, line) for i, line in enumerate(text.splitlines(), start=1) if _is_actionable_py(line)
        ]
        if not actionable:
            continue
        if any(marker in text for marker in GUARD_MARKERS):
            continue
        rel = _rel(path)
        for i, line in actionable:
            violations.append((rel, i, line.strip()[:120]))

    for path in sorted(repo.rglob("*.ts")):
        if _should_skip(path):
            continue
        rel = _rel(path)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        actionable = [
            (i, line)
            for i, line in enumerate(text.splitlines(), start=1)
            if _is_actionable_ts(line, rel=rel)
        ]
        if not actionable:
            continue
        if any(marker in text for marker in GUARD_MARKERS):
            continue
        for i, line in actionable:
            violations.append((rel, i, line.strip()[:120]))

    return violations


def write_badge(*, violations: int, badge_path: Path) -> None:
    badge_path.parent.mkdir(parents=True, exist_ok=True)
    if violations == 0:
        payload = {
            "schemaVersion": 1,
            "label": "LLM calls guarded",
            "message": "100% | enforced: fail-closed",
            "color": "brightgreen",
        }
    else:
        payload = {
            "schemaVersion": 1,
            "label": "LLM calls guarded",
            "message": f"{violations} unguarded | enforced: fail-closed",
            "color": "red",
        }
    badge_path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> int:
    violations: list[tuple[str, int, str]] = []
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in {"Research", "Research_cursor", "founder-os", "kazenai-home", "kazenai-site-v2"}:
            continue
        violations.extend(audit_repo(child))

    badge_path = Path(os.getenv("KAZENAI_BADGE_PATH", ROOT / "badge" / "llm-guard.json"))
    write_badge(violations=len(violations), badge_path=badge_path)

    if not violations:
        print("audit_llm_calls_all: OK (0 unguarded production LLM paths)")
        return 0

    print(f"audit_llm_calls_all: {len(violations)} unguarded LLM call site(s):\n")
    for rel, line_no, snippet in violations:
        print(f"  {rel}:{line_no}: {snippet}")
    print("\nFix: route through kazenai.spine.guarded_llm_call / apply_pre_call_guards.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

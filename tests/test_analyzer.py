"""Attack-path analyzer tests."""

from __future__ import annotations

from agenthound.models import AttackType, NodeKind, Severity
from agenthound.scan import scan


def test_scan_finds_credential_theft_paths() -> None:
    result = scan()
    types = {p.attack_type for p in result.paths}
    assert AttackType.CREDENTIAL_THEFT in types


def test_critical_paths_target_secrets() -> None:
    result = scan()
    critical = [p for p in result.paths if p.severity is Severity.CRITICAL]
    assert critical, "expected at least one critical path in sample env"
    for p in critical:
        terminal = p.steps[-1].node
        # Critical-severity paths in our scoring scheme always end at a Secret
        # (credential theft is the highest base-scored class).
        assert terminal.kind is NodeKind.SECRET, p.title


def test_severity_distribution_is_sane() -> None:
    result = scan()
    assert result.summary.total_paths > 0
    counts = result.summary.by_severity
    assert sum(counts.values()) == result.summary.total_paths


def test_each_path_has_a_mitigation() -> None:
    result = scan()
    for p in result.paths:
        assert p.mitigation, f"path {p.id} missing mitigation"


def test_path_steps_are_contiguous() -> None:
    result = scan()
    for path in result.paths:
        for prev, curr in zip(path.steps, path.steps[1:]):
            assert curr.incoming_edge is not None
            assert curr.incoming_edge.source == prev.node.id
            assert curr.incoming_edge.target == curr.node.id

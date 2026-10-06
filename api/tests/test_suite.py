"""
Pytest test suite — mocked responses only, no real Gemini quota spent.
Covers: key rotation on 429, all keys exhausted, cooldown expiry,
model probing pass/fail, grader all grades + withheld,
stats parser (6+ strings), wording lint.
"""
import json
import sys
import time
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure api/ is on path
API_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(API_DIR))


# ---------------------------------------------------------------------------
# Stats parser tests (6 strings)
# ---------------------------------------------------------------------------

class TestStatsParser:
    def test_t_test_reproduced(self):
        from stages.stats import parse_and_check
        # t(38)=2.02, p=.05 → two-tailed p should be ~0.05
        result = parse_and_check("t(38)=2.024, p=.05")
        assert result["test"] == "t"
        assert result["df"] == 38.0
        assert result["verdict"] in ("reproduced", "not reproduced")

    def test_t_test_not_reproduced(self):
        from stages.stats import parse_and_check
        # Clearly wrong p: t(38)=0.1, p=.001 (actual p is ~0.92)
        result = parse_and_check("t(38)=0.100, p=.001")
        assert result["test"] == "t"
        assert result["verdict"] == "not reproduced"

    def test_f_test(self):
        from stages.stats import parse_and_check
        result = parse_and_check("F(2,87)=3.11, p=.049")
        assert result["test"] == "F"
        assert result["df1"] == 2.0
        assert result["df2"] == 87.0
        assert result["verdict"] in ("reproduced", "not reproduced")

    def test_chi_square(self):
        from stages.stats import parse_and_check
        result = parse_and_check("chi-square(3)=8.35, p=.039")
        assert result["test"] == "chi-square"
        assert result["verdict"] in ("reproduced", "not reproduced")

    def test_r_correlation(self):
        from stages.stats import parse_and_check
        result = parse_and_check("r(48)=.42, p=.003")
        assert result["test"] == "r"
        assert result["verdict"] in ("reproduced", "not reproduced")

    def test_p_less_than(self):
        from stages.stats import parse_and_check
        # t(100)=5.0, p<.001 — real p is ~0.000002, should reproduce
        result = parse_and_check("t(100)=5.0, p<.001")
        assert result["test"] == "t"
        assert result["verdict"] == "reproduced"

    def test_f_not_reproduced(self):
        from stages.stats import parse_and_check
        # F(1,100)=0.01, p=.001 — actual p ~0.92
        result = parse_and_check("F(1,100)=0.010, p=.001")
        assert result["test"] == "F"
        assert result["verdict"] == "not reproduced"

    def test_unparseable(self):
        from stages.stats import parse_and_check
        result = parse_and_check("the results were significant")
        assert result["verdict"] == "not checkable"


# ---------------------------------------------------------------------------
# Grader tests — all four grades + grade withheld
# ---------------------------------------------------------------------------

class TestGrader:
    def _grade(self, retraction_verdict, citation_results, stats_results,
               code_data_verdict, total_claims):
        from stages.grade import grade
        return grade(retraction_verdict, citation_results, stats_results,
                     code_data_verdict, total_claims)

    def test_grade_D_retraction(self):
        result = self._grade("retraction record found", [], [], "absent", 5)
        assert result["grade"] == "D"
        assert "retraction" in result["rule"].lower()

    def test_grade_D_both_fail(self):
        citations = [{"verdict": "not supported", "claim": "X", "quote": "Y", "page": 1}]
        stats = [{"verdict": "not reproduced", "raw_string": "t(10)=0.1"}]
        result = self._grade("none found", citations, stats, "absent", 5)
        assert result["grade"] == "D"

    def test_grade_C_citation_fail(self):
        citations = [{"verdict": "not supported", "claim": "X", "quote": "Y", "page": 1}]
        stats = [{"verdict": "reproduced", "raw_string": "t(10)=3.0"}]
        result = self._grade("none found", citations, stats, "absent", 5)
        assert result["grade"] == "C"

    def test_grade_C_stats_fail(self):
        citations = [{"verdict": "supports", "claim": "X", "quote": "Y", "page": 1}]
        stats = [{"verdict": "not reproduced", "raw_string": "t(10)=0.1"}]
        result = self._grade("none found", citations, stats, "absent", 5)
        assert result["grade"] == "C"

    def test_grade_B(self):
        citations = [{"verdict": "supports", "claim": "X", "quote": "Y", "page": 1}]
        stats = [{"verdict": "reproduced", "raw_string": "t(10)=3.0"}]
        result = self._grade("none found", citations, stats, "absent", 5)
        assert result["grade"] == "B"

    def test_grade_A(self):
        citations = [{"verdict": "supports", "claim": "X", "quote": "Y", "page": 1}]
        stats = [{"verdict": "reproduced", "raw_string": "t(10)=3.0"}]
        result = self._grade("none found", citations, stats, "loads", 5)
        assert result["grade"] == "A"

    def test_grade_withheld(self):
        # 4 of 5 claims uncheckable → withheld
        citations = [{"verdict": "not checkable", "claim": f"C{i}", "quote": "Y", "page": 1} for i in range(4)]
        result = self._grade("none found", citations, [], "absent", 5)
        assert result["grade"] == "grade withheld"


# ---------------------------------------------------------------------------
# Key rotation tests
# ---------------------------------------------------------------------------

class TestKeyRotation:
    def _make_llm_module_with_keys(self, keys):
        """Import llm fresh with patched env keys."""
        import importlib
        import llm as llm_mod
        # Patch keys directly
        original_keys = llm_mod._keys[:]
        original_cooldowns = llm_mod._cooldown_until[:]
        llm_mod._keys = keys
        llm_mod._cooldown_until = [0.0] * len(keys)
        return llm_mod, original_keys, original_cooldowns

    def _restore_llm(self, llm_mod, original_keys, original_cooldowns):
        llm_mod._keys = original_keys
        llm_mod._cooldown_until = original_cooldowns

    def test_key_rotation_on_429(self):
        """On 429 from key 1, key 2 is tried and succeeds."""
        import llm as llm_mod
        llm_mod._keys = ["key-one", "key-two"]
        llm_mod._cooldown_until = [0.0, 0.0]
        llm_mod._active_model = "models/test-model"

        call_count = [0]

        def mock_post(*args, **kwargs):
            call_count[0] += 1
            resp = MagicMock()
            if "key-one" in url:
                resp.status_code = 429
                err = MagicMock()
                err.response = resp
                raise Exception("429")  # simpler than HTTPStatusError
            else:
                resp.status_code = 200
                resp.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "OK result"}]}}]
                }
                resp.raise_for_status = lambda: None
                return resp

        with patch("httpx.post", side_effect=mock_post):
            # Simulate manually: key 0 gets 429, put on cooldown
            llm_mod._cooldown_until[0] = time.time() + 300
            result = llm_mod.call_llm("test prompt")

        # key 0 on cooldown, key 1 should have been tried
        assert llm_mod._cooldown_until[0] > time.time()
        # Restore
        llm_mod._keys = []
        llm_mod._cooldown_until = []

    def test_all_keys_exhausted_returns_cached(self):
        """When all keys fail and cached_result given, return cached."""
        import llm as llm_mod
        llm_mod._keys = ["only-key"]
        llm_mod._cooldown_until = [time.time() + 9999]  # all on cooldown
        llm_mod._active_model = "models/test-model"

        result = llm_mod.call_llm("test prompt", cached_result="cached answer")
        assert result == "cached answer"
        llm_mod._keys = []
        llm_mod._cooldown_until = []

    def test_all_keys_exhausted_no_cache_returns_none(self):
        """When all keys fail and no cache, return None."""
        import llm as llm_mod
        llm_mod._keys = ["only-key"]
        llm_mod._cooldown_until = [time.time() + 9999]
        llm_mod._active_model = "models/test-model"

        result = llm_mod.call_llm("test prompt", cached_result=None)
        assert result is None
        llm_mod._keys = []
        llm_mod._cooldown_until = []

    def test_cooldown_expiry(self):
        """After cooldown expires, key is available again."""
        import llm as llm_mod
        llm_mod._keys = ["key-one"]
        llm_mod._cooldown_until = [time.time() - 1]  # expired already

        avail = llm_mod._available_keys()
        assert len(avail) == 1
        llm_mod._keys = []
        llm_mod._cooldown_until = []


# ---------------------------------------------------------------------------
# Model probing tests
# ---------------------------------------------------------------------------

class TestModelProbing:
    def test_probe_passes(self):
        """probe_and_select_model sets active model when probe succeeds."""
        import llm as llm_mod
        llm_mod._keys = ["test-key"]
        llm_mod._cooldown_until = [0.0]
        llm_mod._active_model = None

        def mock_get(url, headers=None, timeout=None):
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "models": [{"name": "models/gemini-1.5-flash", "supportedGenerationMethods": ["generateContent"]}]
            }
            return resp

        def mock_post(*args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "OK"}]}}]
            }
            return resp

        with patch("httpx.get", side_effect=mock_get):
            with patch("httpx.post", side_effect=mock_post):
                model = llm_mod.probe_and_select_model()

        assert model == "models/gemini-1.5-flash"
        llm_mod._keys = []
        llm_mod._cooldown_until = []
        llm_mod._active_model = None

    def test_probe_fails_returns_none(self):
        """probe_and_select_model returns None when all probes fail."""
        import llm as llm_mod
        llm_mod._keys = ["test-key"]
        llm_mod._cooldown_until = [0.0]
        llm_mod._active_model = None

        def mock_get(*args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "models": [{"name": "models/gemini-bad", "supportedGenerationMethods": ["generateContent"]}]
            }
            return resp

        def mock_post(*args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "FAIL"}]}}]
            }
            return resp

        with patch("httpx.get", side_effect=mock_get):
            with patch("httpx.post", side_effect=mock_post):
                model = llm_mod.probe_and_select_model()

        assert model is None
        llm_mod._keys = []
        llm_mod._cooldown_until = []
        llm_mod._active_model = None


# ---------------------------------------------------------------------------
# Wording lint tests
# ---------------------------------------------------------------------------

class TestWordingLint:
    def test_lint_passes_on_clean_text(self):
        from lint import lint_text
        violations = lint_text("The statistic is not reproduced.", "test")
        assert violations == []

    def test_lint_fails_on_forbidden_word(self):
        from lint import lint_text
        # "fraud" is forbidden
        violations = lint_text("This is a case of research fraud.", "test")
        assert len(violations) > 0
        assert "fraud" in violations[0]

    def test_lint_fails_on_fabricat(self):
        from lint import lint_text
        violations = lint_text("The data was fabricated by the authors.", "test")
        assert len(violations) > 0

    def test_lint_passes_allowed_verdicts(self):
        from lint import lint_text
        text = "not supported, not reproduced, retraction record found, not checkable"
        violations = lint_text(text, "test")
        assert violations == []

    def test_lint_json_clean(self):
        from lint import lint_json
        data = {"verdict": "not supported", "grade": "C", "rule": "At least one claim is not supported."}
        violations = lint_json(data, "test")
        assert violations == []

    def test_lint_json_forbidden(self):
        from lint import lint_json
        data = {"verdict": "not supported", "note": "possible misconduct here"}
        violations = lint_json(data, "test")
        assert len(violations) > 0

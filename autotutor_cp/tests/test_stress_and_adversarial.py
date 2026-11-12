"""Empirical Adversarial Stress & Route Integrity Tests.
Tests concurrency, event loop responsiveness, cache clearing, and edge cases.
"""
import asyncio
import time
import pytest
import httpx
from starlette.testclient import TestClient

from autotutor_cp.api_server import app
from autotutor_cp.core import problem_bank, library
from autotutor_cp.core.knowledge import KnowledgeBase


@pytest.fixture
def test_client():
    return TestClient(app)


class TestConcurrencyAndEventLoop:
    """Stress tests verifying concurrency and event loop behavior under load."""

    @pytest.mark.anyio
    async def test_concurrent_api_calls_standard_profile(self):
        """Execute 60 concurrent requests across /api/progress, /api/problems, and /api/library/search
        with a standard profile (12 KB payload).
        Verifies that asyncio event loop remains responsive (< 50ms lag).
        """
        transport = httpx.ASGITransport(app=app)
        max_lag = 0.0
        stop_monitor = False

        async def loop_lag_monitor():
            nonlocal max_lag
            interval = 0.005  # 5ms
            while not stop_monitor:
                t0 = time.perf_counter()
                await asyncio.sleep(interval)
                elapsed = time.perf_counter() - t0
                lag = elapsed - interval
                if lag > max_lag:
                    max_lag = lag

        monitor_task = asyncio.create_task(loop_lag_monitor())

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            endpoints = [
                "/api/progress",
                "/api/problems",
                "/api/library/search?q=grafo",
            ]
            # 20 concurrent requests per endpoint = 60 concurrent requests
            tasks = []
            for ep in endpoints:
                for _ in range(20):
                    tasks.append(client.get(ep, headers={"x-profile-id": "2195f7d0e7f04e138919af3b48c2b68f"}))

            t_start = time.perf_counter()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_duration = time.perf_counter() - t_start

        stop_monitor = True
        await monitor_task

        # Assert all requests succeeded
        assert len(responses) == 60
        for i, resp in enumerate(responses):
            assert not isinstance(resp, Exception), f"Request {i} raised exception: {resp}"
            assert resp.status_code == 200, f"Request {i} failed with status {resp.status_code}: {resp.text}"

        print(f"\n[STANDARD PROFILE] 60 concurrent requests completed in {total_duration:.3f}s")
        print(f"[STANDARD PROFILE] Max event loop lag measured: {max_lag * 1000:.2f}ms")

        # Standard profile: latency should be under 3.0s and event loop lag under 100ms
        assert total_duration < 3.0, f"Total duration too high: {total_duration:.3f}s >= 3.0s"
        assert max_lag < 0.100, f"Event loop lag too high: {max_lag * 1000:.2f}ms >= 100ms"

    @pytest.mark.anyio
    async def test_adversarial_bloated_profile_stress(self):
        """Adversarial stress test on the active profile (21.3 MB payload).
        Measures GIL contention and documents event loop lag under heavy JSON parsing.
        """
        transport = httpx.ASGITransport(app=app)
        max_lag = 0.0
        stop_monitor = False

        async def loop_lag_monitor():
            nonlocal max_lag
            interval = 0.005
            while not stop_monitor:
                t0 = time.perf_counter()
                await asyncio.sleep(interval)
                elapsed = time.perf_counter() - t0
                lag = elapsed - interval
                if lag > max_lag:
                    max_lag = lag

        monitor_task = asyncio.create_task(loop_lag_monitor())

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            t0 = time.perf_counter()
            tasks = [
                client.get("/api/progress", headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"})
                for _ in range(20)
            ]
            responses = await asyncio.gather(*tasks)
            elapsed = time.perf_counter() - t0

        stop_monitor = True
        await monitor_task

        for r in responses:
            assert r.status_code == 200
            assert len(r.content) < 2048

        print(f"\n[BLOATED PROFILE STRESS] 20 concurrent /api/progress completed in {elapsed:.3f}s (avg {elapsed/20*1000:.2f}ms/req)")
        print(f"[BLOATED PROFILE STRESS] Max event loop lag measured: {max_lag * 1000:.2f}ms")

        # Empirically verify that responses all succeed with <2KB payload
        assert len(responses) == 20


class TestCachePurgeAndRepopulation:
    """Verifies that clear_cache() properly purges cached data and repopulates correctly."""

    def test_problem_bank_cache_purge(self):
        problem_bank.clear_cache()
        info_before = problem_bank.load_problems.cache_info()
        assert info_before.currsize == 0

        p1 = problem_bank.load_problems()
        assert len(p1) > 0
        info_after_1 = problem_bank.load_problems.cache_info()
        assert info_after_1.currsize == 1
        assert info_after_1.misses >= 1

        p2 = problem_bank.load_problems()
        info_after_2 = problem_bank.load_problems.cache_info()
        assert info_after_2.hits >= 1
        assert p1 == p2

        problem_bank.clear_cache()
        info_purged = problem_bank.load_problems.cache_info()
        assert info_purged.currsize == 0
        assert info_purged.hits == 0
        assert info_purged.misses == 0

        p3 = problem_bank.load_problems()
        assert len(p3) == len(p1)
        info_reloaded = problem_bank.load_problems.cache_info()
        assert info_reloaded.currsize == 1
        assert info_reloaded.misses == 1

    def test_library_cache_purge(self):
        library.clear_cache()
        assert library.resources.cache_info().currsize == 0
        assert library.deep_guides.cache_info().currsize == 0

        r1 = library.resources()
        g1 = library.deep_guides()
        assert len(r1) > 0
        assert len(g1) > 0
        assert library.resources.cache_info().currsize == 1
        assert library.deep_guides.cache_info().currsize == 1

        library.clear_cache()
        assert library.resources.cache_info().currsize == 0
        assert library.deep_guides.cache_info().currsize == 0

        r2 = library.resources()
        g2 = library.deep_guides()
        assert len(r2) == len(r1)
        assert len(g2) == len(g1)
        assert library.resources.cache_info().currsize == 1
        assert library.deep_guides.cache_info().currsize == 1

    def test_knowledge_base_cache_purge(self):
        from pathlib import Path
        real_kb_path = Path("autotutor_cp/data/knowledge.sqlite3").resolve()
        kb = KnowledgeBase(real_kb_path)
        KnowledgeBase.clear_stats_cache()
        assert len(KnowledgeBase._stats_cache) == 0

        s1 = kb.stats()
        assert isinstance(s1, dict)
        assert s1["documents"] > 0
        assert len(KnowledgeBase._stats_cache) == 1

        KnowledgeBase.clear_stats_cache(kb.path)
        assert len(KnowledgeBase._stats_cache) == 0

        s2 = kb.stats()
        assert s2["documents"] == s1["documents"]
        assert len(KnowledgeBase._stats_cache) == 1

        KnowledgeBase.clear_stats_cache()
        assert len(KnowledgeBase._stats_cache) == 0


class TestEdgeCaseAndBackwardCompatibility:
    """Verifies backward compatibility and error resilience on invalid inputs."""

    def test_progress_include_materials_backward_compatibility(self, test_client):
        # 1. Default request: lightweight
        resp_light = test_client.get(
            "/api/progress",
            headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"},
        )
        assert resp_light.status_code == 200
        data_light = resp_light.json()
        assert len(resp_light.content) < 2048
        assert data_light["materials_count"] > 0
        assert len(data_light["materials"]) <= 4
        for m in data_light["materials"]:
            assert "payload" not in m
            assert "id" in m
            assert "title" in m

        # 2. include_materials=true: full backward compatibility
        resp_full = test_client.get(
            "/api/progress?include_materials=true&limit=100",
            headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"},
        )
        assert resp_full.status_code == 200
        data_full = resp_full.json()
        assert len(resp_full.content) > 100000, f"Expected full payload >100KB, got {len(resp_full.content)}"
        assert data_full["materials_count"] == len(data_full["materials"])
        for m in data_full["materials"]:
            assert "payload" in m
            assert "content" in m["payload"] or "concept" in m["payload"]
            assert "id" in m
            assert "title" in m

        assert "saved_materials" in data_full
        assert len(data_full["saved_materials"]) == len(data_full["materials"])

    def test_invalid_routes_return_graceful_404(self, test_client):
        resp = test_client.get("/api/nonexistent_route_404")
        assert resp.status_code == 404

        resp_mat = test_client.get(
            "/api/progress/materials/nonexistent_material_id_99999",
            headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"},
        )
        assert resp_mat.status_code == 404
        assert resp_mat.json() == {"error": "Material não encontrado."}

        resp_prob = test_client.get("/api/problems/nonexistent_prob_xyz")
        assert resp_prob.status_code == 404
        assert "não encontrado" in resp_prob.json().get("error", "")

    def test_malformed_query_params_graceful_fallback(self, test_client):
        resp1 = test_client.get(
            "/api/progress?limit=-50&history_limit=invalid_number",
            headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"},
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert "materials" in data1

        resp2 = test_client.get(
            "/api/progress/materials?limit=999999&offset=-5",
            headers={"x-profile-id": "c3c9024f085b4f4c83120167003900a8"},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["limit"] <= 100
        assert data2["offset"] == 0

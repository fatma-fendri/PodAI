from app.agent import add_source, finalize


def make_sources(n):
    return [
        {"title": f"S{i}", "url": f"https://example.org/{i}", "origin": "Knowledge base"}
        for i in range(1, n + 1)
    ]


def test_renumbers_by_order_of_appearance():
    answer, used = finalize("A [3]. B [1].", make_sources(3))
    assert answer == "A [1]. B [2]."
    assert [s["title"] for s in used] == ["S3", "S1"]


def test_unknown_citation_is_removed():
    answer, used = finalize("A [9].", make_sources(2))
    assert "[9]" not in answer
    assert used == []


def test_comma_citation_is_split():
    answer, used = finalize("A [2,3]. B [1].", make_sources(3))
    assert answer == "A [1][2]. B [3]."
    assert [s["title"] for s in used] == ["S2", "S3", "S1"]


def test_same_url_with_http_and_https_is_one_source():
    sources = []
    first = add_source(sources, "Ingrown", "https://www.mayoclinic.org/x", "Trusted Websites")
    second = add_source(sources, "Ingrown", "http://www.mayoclinic.org/x", "Trusted Websites")
    assert first == second == 1
    assert len(sources) == 1
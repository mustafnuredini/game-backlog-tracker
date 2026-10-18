import main


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "results": [
                {
                    "name": "Elden Ring",
                    "released": "2022-02-25",
                    "rating": 4.38,
                }
            ]
        }

# Verify that game details display correctly


def test_search_games_prints_results(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    def fake_get(url, params, timeout):
        assert url == main.API_URL
        assert params["search"] == "Elden Ring"
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr(main.requests, "get", fake_get)

    main.search_games("Elden Ring")

    output = capsys.readouterr().out

    assert "Elden Ring" in output
    assert "2022-02-25" in output
    assert "4.38" in output

# Verify empty search results are handled


def test_search_games_no_results(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    class EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"results": []}

    monkeypatch.setattr(
        main.requests,
        "get",
        lambda *args, **kwargs: EmptyResponse(),
    )

    main.search_games("Some nonexistent game")

    output = capsys.readouterr().out

    assert "No games found." in output

# Verify missing credentials are handled


def test_search_games_missing_api_key(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", None)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("API request should not be made")

    monkeypatch.setattr(main.requests, "get", fail_if_called)

    main.search_games("Elden Ring")

    output = capsys.readouterr().out

    assert "RAWG_API_KEY is missing" in output

# Verify blank input is rejected


def test_search_games_empty_name(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("API request should not be made")

    monkeypatch.setattr(main.requests, "get", fail_if_called)

    main.search_games("   ")

    output = capsys.readouterr().out

    assert "Please enter a game name." in output

# Verify network timeouts are handled


def test_search_games_timeout(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    def raise_timeout(*args, **kwargs):
        raise main.requests.exceptions.Timeout

    monkeypatch.setattr(main.requests, "get", raise_timeout)

    main.search_games("Elden Ring")

    output = capsys.readouterr().out

    assert "The request timed out." in output

# Verify that HTTP errors are handled


def test_search_games_http_error(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    def raise_http_error(*args, **kwargs):
        response = main.requests.Response()
        response.status_code = 500
        raise main.requests.exceptions.HTTPError(
            "500 Server Error",
            response=response,
        )

    monkeypatch.setattr(
        main.requests, "get", raise_http_error
    )

    main.search_games("Elden Ring")

    output = capsys.readouterr().out

    assert "API returned an HTTP error:" in output

# Verify that invalid JSON is handled


def test_search_games_invalid_json(monkeypatch, capsys):
    monkeypatch.setattr(main, "API_KEY", "test-key")

    class InvalidJSONResponse:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("Invalid JSON")

    monkeypatch.setattr(
        main.requests,
        "get",
        lambda *args, **kwargs: InvalidJSONResponse(),
    )

    main.search_games("Elden Ring")

    output = capsys.readouterr().out

    assert "RAWG returned invalid JSON." in output

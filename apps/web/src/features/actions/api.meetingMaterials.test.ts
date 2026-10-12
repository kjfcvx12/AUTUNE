import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/api/client";

import { getMeetingMaterials } from "./api";

// The uploaded materials nearest a meeting's title (#817). The one thing the
// call has to get right is what it sends: the meeting's id in the path and
// nothing else -- no body, no query -- so that nothing said in the meeting
// can ride along to be searched with.

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("getMeetingMaterials", () => {
  it("sends the meeting's id in the path, and no body and no query", async () => {
    const answer = {
      team_id: "team_a",
      asked: true,
      hits: [],
      notice: null,
      more: false,
      max_question_chars: 300,
    };
    const fetched = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(
      async () =>
        new Response(JSON.stringify(answer), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetched);

    const got = await getMeetingMaterials("mtg 1");

    expect(got).toEqual(answer);
    expect(fetched).toHaveBeenCalledTimes(1);
    const [url, init] = fetched.mock.calls[0] ?? [];
    expect(url).toMatch(/\/api\/extraction\/meetings\/mtg%201\/materials\/near-title$/);
    expect(String(url)).not.toContain("?");
    expect(init?.method ?? "GET").toBe("GET");
    expect(init?.body).toBeUndefined();
  });

  it("takes one argument: there is nowhere to hand it a line", () => {
    expect(getMeetingMaterials.length).toBe(1);
  });

  it("reads the bare 404 of a server with uploads off as a refusal that is not ours", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ detail: "Not Found" }), {
            status: 404,
            statusText: "Not Found",
          }),
      ),
    );

    const refused = await getMeetingMaterials("mtg_1").catch((cause: unknown) => cause);

    expect(refused).toBeInstanceOf(ApiError);
    expect((refused as ApiError).status).toBe(404);
    expect((refused as ApiError).code).toBe("unknown");
  });
});

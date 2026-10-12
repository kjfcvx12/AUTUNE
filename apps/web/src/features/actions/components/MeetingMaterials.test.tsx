import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, expectTypeOf, it, vi } from "vitest";

import { ApiError } from "@/shared/api/client";

import type { MeetingMaterialsAnswer } from "../types";
import { MeetingMaterials } from "./MeetingMaterials";

// The box of a team's uploaded materials beside one meeting (#817). What is
// under test is that it asks with the meeting's id and nothing else -- so
// nothing said in the meeting can be searched with -- that it is not there
// at all where the server refuses, and that a typed question goes where the
// 자료 screen's goes. Every word here is made up.

const near = vi.fn();
const search = vi.fn();
vi.mock("../api", () => ({
  getMeetingMaterials: (...sent: unknown[]) => near(...sent),
  searchMaterials: (teamId: string, question: string) => search(teamId, question),
}));

const answer = (over: Partial<MeetingMaterialsAnswer> = {}): MeetingMaterialsAnswer => ({
  team_id: "team_a",
  asked: true,
  hits: [
    { material_id: "mat_plan", title: "분기 계획", excerpt: "…출시는 11월 둘째 주로 잡는다." },
    { material_id: "mat_notes", title: "회고 메모", excerpt: "출시 뒤 한 주는 <b>기능 동결</b>" },
  ],
  notice: null,
  more: false,
  max_question_chars: 300,
  ...over,
});

const nearTitle = () => screen.findByRole("region", { name: "회의 제목과 가까운 자료" });

afterEach(() => {
  cleanup();
  near.mockReset();
  search.mockReset();
});

describe("MeetingMaterials, what it asks with", () => {
  it("takes the meeting's id and no other prop", () => {
    // A prop that could carry a spoken line into here would be the search
    // privacy.md does not allow.
    expectTypeOf<ComponentProps<typeof MeetingMaterials>>().toEqualTypeOf<{ meetingId: string }>();
  });

  it("asks once, with the id alone", async () => {
    near.mockResolvedValue(answer());

    render(<MeetingMaterials meetingId="mtg_1" />);
    await nearTitle();

    expect(near.mock.calls).toEqual([["mtg_1"]]);
    expect(search).not.toHaveBeenCalled();
  });

  it("says that what was said in the meeting is not searched with", async () => {
    near.mockResolvedValue(answer());

    render(<MeetingMaterials meetingId="mtg_1" />);

    expect(within(await nearTitle()).getByText(/회의에서 말한 내용으로는 찾지\s+않습니다/)).toBeTruthy();
  });
});

describe("MeetingMaterials, what it shows", () => {
  it("lists each material's title and its excerpt as text", async () => {
    near.mockResolvedValue(answer());

    render(<MeetingMaterials meetingId="mtg_1" />);
    const region = await nearTitle();

    expect(within(region).getByText("분기 계획")).toBeTruthy();
    expect(within(region).getByText("…출시는 11월 둘째 주로 잡는다.")).toBeTruthy();
    // Markup in an excerpt is text, and a hit links to nothing.
    expect(within(region).getByText("출시 뒤 한 주는 <b>기능 동결</b>")).toBeTruthy();
    expect(region.querySelector("b, a")).toBeNull();
  });

  it("shows the server's notice as it is", async () => {
    near.mockResolvedValue(answer({ notice: "별표(*)로 보이는 부분은 가려진 값일 수 있습니다." }));

    render(<MeetingMaterials meetingId="mtg_1" />);

    expect(
      within(await nearTitle()).getByText("별표(*)로 보이는 부분은 가려진 값일 수 있습니다."),
    ).toBeTruthy();
  });

  it("says a meeting with no title was not searched, and still has the box", async () => {
    near.mockResolvedValue(answer({ asked: false, hits: [] }));

    render(<MeetingMaterials meetingId="mtg_1" />);
    const region = await nearTitle();

    expect(within(region).getByText("회의에 제목이 없어 가까운 자료를 찾지 않았습니다.")).toBeTruthy();
    expect(screen.getByRole("form", { name: "자료 검색" })).toBeTruthy();
  });

  it("says so when the title is near nothing, unless the server's notice already does", async () => {
    near.mockResolvedValue(answer({ hits: [] }));
    render(<MeetingMaterials meetingId="mtg_1" />);
    expect(within(await nearTitle()).getByText("회의 제목과 가까운 자료가 없습니다.")).toBeTruthy();
    cleanup();

    near.mockResolvedValue(answer({ hits: [], notice: "충분히 가까운 내용을 찾지 못했습니다." }));
    render(<MeetingMaterials meetingId="mtg_1" />);
    const region = await nearTitle();
    expect(within(region).getByText("충분히 가까운 내용을 찾지 못했습니다.")).toBeTruthy();
    expect(within(region).queryByText("회의 제목과 가까운 자료가 없습니다.")).toBeNull();
  });
});

describe("MeetingMaterials, where there is nothing to show", () => {
  it.each([
    ["uploads are off", new ApiError(404, "unknown", "Not Found", {})],
    ["the reader may not read the meeting", new ApiError(404, "not_found", "meeting", {})],
    ["the request failed", new Error("network")],
  ])("draws nothing when %s", async (_name, cause) => {
    near.mockRejectedValue(cause);

    const { container } = render(<MeetingMaterials meetingId="mtg_1" />);
    await waitFor(() => expect(near).toHaveBeenCalled());
    await Promise.resolve();

    expect(container.innerHTML).toBe("");
  });

  it("draws nothing before the server has answered", () => {
    near.mockReturnValue(new Promise(() => {}));

    const { container } = render(<MeetingMaterials meetingId="mtg_1" />);

    expect(container.innerHTML).toBe("");
  });

  it("does not show one meeting's materials beside another", async () => {
    near.mockResolvedValueOnce(answer());
    const { container, rerender } = render(<MeetingMaterials meetingId="mtg_1" />);
    await nearTitle();

    near.mockReturnValue(new Promise(() => {}));
    rerender(<MeetingMaterials meetingId="mtg_2" />);

    expect(container.innerHTML).toBe("");
    expect(near.mock.calls).toEqual([["mtg_1"], ["mtg_2"]]);
  });
});

describe("MeetingMaterials, a question a member types", () => {
  it("goes to the team's search with the words typed, and to nothing else", async () => {
    near.mockResolvedValue(answer({ max_question_chars: 120 }));
    search.mockResolvedValue({
      hits: [{ material_id: "mat_budget", title: "예산", excerpt: "장비 구매 1200만원" }],
      notice: null,
      more: false,
    });
    render(<MeetingMaterials meetingId="mtg_1" />);
    await nearTitle();
    const box = screen.getByLabelText("자료에 물을 내용") as HTMLInputElement;
    expect(box.maxLength).toBe(120);

    fireEvent.change(box, { target: { value: "장비 예산" } });
    fireEvent.click(screen.getByRole("button", { name: "찾기" }));

    const found = await screen.findByRole("region", { name: "찾은 내용" });
    expect(within(found).getByText("장비 구매 1200만원")).toBeTruthy();
    expect(search.mock.calls).toEqual([["team_a", "장비 예산"]]);
    // The typed question does not ask the title's route again.
    expect(near).toHaveBeenCalledTimes(1);
  });
});

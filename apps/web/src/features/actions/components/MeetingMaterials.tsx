"use client";

import { useEffect, useState } from "react";

import { getMeetingMaterials, searchMaterials } from "../api";
import type { MeetingMaterialsAnswer } from "../types";
import { MaterialSearch } from "./MaterialSearch";

/**
 * The team's uploaded materials beside one meeting (#817): those nearest the
 * meeting's title, and the 자료 screen's question box under them.
 *
 * **Nothing said in the meeting is searched with.** This component is given
 * the meeting's id and nothing else -- no transcript row, no selection -- and
 * the server reads the title itself. What a member types into the box is
 * their own question, sent as the 자료 screen sends one. `privacy.md` does
 * not let live transcript text be searched against materials; a prop that
 * carries a spoken line into here would be that search.
 *
 * It draws nothing until the server has answered, and nothing at all where
 * it refuses -- uploads off, a meeting the reader may not read, a failure --
 * so the screen that holds it is as it was. What it shows is masked text, as
 * the box below says.
 */
export function MeetingMaterials({ meetingId }: { meetingId: string }) {
  const [answer, setAnswer] = useState<{ of: string; got: MeetingMaterialsAnswer } | null>(null);

  useEffect(() => {
    let current = true;
    getMeetingMaterials(meetingId).then(
      (got) => {
        if (current) setAnswer({ of: meetingId, got });
      },
      () => {
        if (current) setAnswer(null);
      },
    );
    return () => {
      current = false;
    };
  }, [meetingId]);

  // An answer belongs to the meeting it was asked for: in the render where
  // the id has changed, the earlier meeting's materials are not shown.
  if (answer === null || answer.of !== meetingId) return null;
  const { got } = answer;
  const meta = { fontSize: "var(--text-metaSmall)" } as const;

  return (
    <section aria-label="회의 자료" className="flex flex-col gap-3">
      <div role="region" aria-label="회의 제목과 가까운 자료" className="flex flex-col gap-2">
        <span className="text-[var(--color-ink)]">회의 제목과 가까운 자료</span>
        <p className="text-[var(--color-ink-muted)]" style={meta}>
          회의 제목으로 팀이 올린 파일에서 찾은 결과입니다. 회의에서 말한 내용으로는 찾지
          않습니다.
        </p>
        {got.notice ? (
          <p className="text-[var(--color-ink-muted)]" style={meta}>
            {got.notice}
          </p>
        ) : null}
        {got.hits.length > 0 ? (
          <ul className="flex flex-col gap-2">
            {got.hits.map((hit) => (
              <li
                key={hit.material_id}
                className="flex flex-col gap-1 border-l-2 border-[var(--color-hairline)] pl-3"
              >
                <span className="text-[var(--color-ink)]">{hit.title}</span>
                <span
                  className="whitespace-pre-line break-words text-[var(--color-ink-muted)]"
                  style={meta}
                >
                  {hit.excerpt}
                </span>
              </li>
            ))}
          </ul>
        ) : got.asked ? (
          // A notice that came with no hit already says why there is none.
          got.notice ? null : (
            <p className="text-[var(--color-ink-muted)]" style={meta}>
              회의 제목과 가까운 자료가 없습니다.
            </p>
          )
        ) : (
          <p className="text-[var(--color-ink-muted)]" style={meta}>
            회의에 제목이 없어 가까운 자료를 찾지 않았습니다.
          </p>
        )}
        {got.more && got.hits.length > 0 ? (
          <p className="text-[var(--color-ink-muted)]" style={meta}>
            이 밖에도 가까운 자료가 더 있습니다. 아래에서 직접 찾아볼 수 있습니다.
          </p>
        ) : null}
      </div>
      <MaterialSearch
        limit={got.max_question_chars}
        onSearch={(question) => searchMaterials(got.team_id, question)}
        removed={[]}
      />
    </section>
  );
}

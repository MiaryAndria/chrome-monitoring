import React from "react";

function renderInline(text, keyPrefix) {
    const parts = [];
    const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
    let last = 0;
    let match;
    let i = 0;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > last) parts.push(text.slice(last, match.index));

        const token = match[0];
        if (token.startsWith("**")) {
            parts.push(
                <strong key={`${keyPrefix}-${i++}`} className="font-semibold text-zinc-100">
                    {token.slice(2, -2)}
                </strong>
            );
        } else {
            parts.push(
                <code
                    key={`${keyPrefix}-${i++}`}
                    className="px-1 py-0.5 rounded bg-black/40 text-cyan-300 text-[12px] font-mono"
                >
                    {token.slice(1, -1)}
                </code>
            );
        }
        last = match.index + token.length;
    }

    if (last < text.length) parts.push(text.slice(last));
    return parts;
}

export default function MarkdownLite({ text }) {
    const lines = (text || "").split("\n");
    const blocks = [];
    let list = null;

    const flushList = () => {
        if (!list) return;
        const Tag = list.ordered ? "ol" : "ul";
        blocks.push(
            <Tag
                key={`list-${blocks.length}`}
                className={`${list.ordered ? "list-decimal" : "list-disc"} ml-5 space-y-1 marker:text-cyan-400`}
            >
                {list.items.map((item, idx) => (
                    <li key={idx} className="pl-1">
                        {renderInline(item, `li-${blocks.length}-${idx}`)}
                    </li>
                ))}
            </Tag>
        );
        list = null;
    };

    lines.forEach((raw, idx) => {
        const line = raw.replace(/\s+$/, "");

        if (!line.trim()) {
            flushList();
            return;
        }

        if (/^---+$/.test(line.trim())) {
            flushList();
            blocks.push(<hr key={`hr-${idx}`} className="border-white/10 my-3" />);
            return;
        }

        const heading = line.match(/^(#{1,4})\s+(.*)$/);
        if (heading) {
            flushList();
            const level = heading[1].length;
            const cls =
                level <= 2
                    ? "text-[13px] font-bold uppercase tracking-wide text-cyan-300 mt-3 pb-1 border-b border-cyan-500/20 first:mt-0"
                    : "text-[13px] font-semibold text-zinc-100 mt-2";
            blocks.push(
                <p key={`h-${idx}`} className={cls}>
                    {renderInline(heading[2], `h-${idx}`)}
                </p>
            );
            return;
        }

        const ul = line.match(/^(\*|-|•)\s+(.*)$/);
        if (ul) {
            if (!list || list.ordered) {
                flushList();
                list = { ordered: false, items: [] };
            }
            list.items.push(ul[2]);
            return;
        }

        const ol = line.match(/^(\d+)[.)]\s+(.*)$/);
        if (ol) {
            if (!list || !list.ordered) {
                flushList();
                list = { ordered: true, items: [] };
            }
            list.items.push(ol[2]);
            return;
        }

        flushList();
        blocks.push(
            <p key={`p-${idx}`} className="leading-relaxed text-zinc-300">
                {renderInline(line, `p-${idx}`)}
            </p>
        );
    });

    flushList();

    return <div className="space-y-2 text-[13px]">{blocks}</div>;
}

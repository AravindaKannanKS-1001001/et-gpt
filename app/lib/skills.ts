import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import matter from "gray-matter";

// Skills use the SKILL.md format (name + description frontmatter, body loaded on demand).
const DIR = join(process.cwd(), "skills");
export type Skill = { name: string; description: string; body: string };

let cached: Skill[] | undefined;
export function loadSkills(): Skill[] {
  cached ??= readdirSync(DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const f = matter(readFileSync(join(DIR, d.name, "SKILL.md"), "utf8"));
      return { body: f.content.trim(), description: String(f.data.description), name: String(f.data.name) };
    });
  return cached;
}

export function skillsPrompt() {
  const list = loadSkills().map((s) => `- ${s.name}: ${s.description}`).join("\n");
  return `Skills (call loadSkill(name) to read one before following it):\n${list}`;
}

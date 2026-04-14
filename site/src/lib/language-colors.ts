export const LANGUAGE_COLORS: Record<string, string> = {
  python: '#3572A5',
  javascript: '#f7df1e',
  typescript: '#3178c6',
  go: '#00ADD8',
  rust: '#DEA584',
  java: '#b07219',
  csharp: '#178600',
  php: '#4F5D95',
  ruby: '#701516',
  swift: '#F05138',
  kotlin: '#A97BFF',
  cpp: '#555555',
};

export const LANGUAGE_NAMES: Record<string, string> = {
  python: 'Python',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  go: 'Go',
  rust: 'Rust',
  java: 'Java',
  csharp: 'C#',
  php: 'PHP',
  ruby: 'Ruby',
  swift: 'Swift',
  kotlin: 'Kotlin',
  cpp: 'C++',
};

export const langColor = (slug: string): string =>
  LANGUAGE_COLORS[slug] ?? '#8a8a84';

export const langName = (slug: string): string =>
  LANGUAGE_NAMES[slug] ?? slug.charAt(0).toUpperCase() + slug.slice(1);

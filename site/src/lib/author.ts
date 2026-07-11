// Single source of truth for authorship + publisher identity (E-E-A-T).
// Referenced by PostLayout (Article schema + byline), the author bio page,
// and the About page. Update the name/role/links here and every surface follows.

export const SITE_URL = 'https://devnook.dev';

export const AUTHOR = {
  name: 'Syed J.',
  role: 'Founder & Editor',
  slug: 'syed-j',
  path: '/about/syed-j/',
  url: `${SITE_URL}/about/syed-j/`,
  // Real profile URLs (GitHub, LinkedIn, X, etc.) strengthen author E-E-A-T.
  // Add them here and they flow into the Person schema automatically.
  sameAs: [] as string[],
};

export const ORGANIZATION = {
  name: 'DevNook',
  url: SITE_URL,
  logo: `${SITE_URL}/logo.svg`,
};

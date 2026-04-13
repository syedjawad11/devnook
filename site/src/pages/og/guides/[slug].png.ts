import { getCollection } from 'astro:content';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

const outfitCss = await fetch(
  'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap'
).then((res) => res.text());

const outfitFontUrl = outfitCss.match(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/)?.[1];

if (!outfitFontUrl) {
  throw new Error('Failed to extract Outfit font URL from Google Fonts CSS');
}

const outfitFont = await fetch(outfitFontUrl).then((res) => res.arrayBuffer());

export async function getStaticPaths() {
  const guides = await getCollection('guides');
  return guides.map((guide) => ({
    params: { slug: guide.slug },
    props: { guide },
  }));
}

export async function GET({ props }: { props: { guide: any } }) {
  const { guide } = props;
  const { title, description, category } = guide.data;

  const svg = await satori(
    {
      type: 'div',
      props: {
        style: {
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          backgroundColor: '#0d0d0d',
          padding: '64px',
          fontFamily: 'Outfit',
        },
        children: [
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      width: '48px',
                      height: '48px',
                      borderRadius: '8px',
                      backgroundColor: '#6ee7b7',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '28px',
                      fontWeight: '700',
                      color: '#0d0d0d',
                    },
                    children: 'DN',
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '24px',
                      fontWeight: '600',
                      color: '#e8e8e8',
                    },
                    children: 'DevNook',
                  },
                },
              ],
            },
          },
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                flexDirection: 'column',
                gap: '24px',
                maxWidth: '1000px',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      display: 'flex',
                      padding: '8px 16px',
                      backgroundColor: '#6ee7b7',
                      color: '#0d0d0d',
                      fontSize: '18px',
                      fontWeight: '600',
                      borderRadius: '8px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    },
                    children: category || 'Guide',
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '64px',
                      fontWeight: '700',
                      color: '#e8e8e8',
                      lineHeight: '1.1',
                      letterSpacing: '-0.02em',
                    },
                    children: title,
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '28px',
                      fontWeight: '400',
                      color: '#8a8a8a',
                      lineHeight: '1.4',
                    },
                    children: description,
                  },
                },
              ],
            },
          },
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                fontSize: '20px',
                color: '#8a8a8a',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    children: 'devnook.dev',
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      width: '4px',
                      height: '4px',
                      borderRadius: '50%',
                      backgroundColor: '#8a8a8a',
                    },
                  },
                },
                {
                  type: 'div',
                  props: {
                    children: 'Developer Resources',
                  },
                },
              ],
            },
          },
        ],
      },
    },
    {
      width: 1200,
      height: 630,
      fonts: [
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 400,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 600,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 700,
          style: 'normal',
        },
      ],
    }
  );

  const resvg = new Resvg(svg, {
    fitTo: {
      mode: 'width',
      value: 1200,
    },
  });

  const png = resvg.render().asPng();

  return new Response(png, {
    headers: {
      'Content-Type': 'image/png',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
}
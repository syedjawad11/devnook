import { getCollection } from 'astro:content';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

export async function getStaticPaths() {
  const tools = await getCollection('tools');
  return tools.map((tool) => ({
    params: { slug: tool.slug },
    props: { tool },
  }));
}

export async function GET({ props }: { props: any }) {
  const { tool } = props;
  const { title, description } = tool.data;

  // Use Google Fonts API v1 (serves TTF by default — Satori's OpenType parser can't handle woff2)
  const fontCss = await fetch(
    'https://fonts.googleapis.com/css?family=Outfit:400,700'
  ).then((res) => res.text());

  const fontUrl = fontCss.match(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/)?.[1];

  if (!fontUrl) {
    throw new Error('Failed to extract font URL from Google Fonts CSS');
  }

  const fontBuffer = await fetch(fontUrl).then((res) => res.arrayBuffer());

  const svg = await satori(
    {
      type: 'div',
      props: {
        style: {
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
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
                marginBottom: '48px',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      width: '48px',
                      height: '48px',
                      backgroundColor: '#6ee7b7',
                      borderRadius: '8px',
                      marginRight: '16px',
                    },
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '32px',
                      fontWeight: 700,
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
                alignItems: 'center',
                marginBottom: '24px',
              },
              children: {
                type: 'div',
                props: {
                  style: {
                    fontSize: '20px',
                    fontWeight: 700,
                    color: '#6ee7b7',
                    backgroundColor: 'rgba(110, 231, 183, 0.1)',
                    padding: '8px 16px',
                    borderRadius: '8px',
                  },
                  children: 'Tool',
                },
              },
            },
          },
          {
            type: 'div',
            props: {
              style: {
                fontSize: '64px',
                fontWeight: 700,
                color: '#e8e8e8',
                lineHeight: 1.2,
                marginBottom: '24px',
                maxWidth: '1000px',
              },
              children: title,
            },
          },
          {
            type: 'div',
            props: {
              style: {
                fontSize: '28px',
                fontWeight: 400,
                color: '#8a8a8a',
                lineHeight: 1.4,
                maxWidth: '900px',
              },
              children: description,
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
          data: fontBuffer,
          weight: 400,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: fontBuffer,
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
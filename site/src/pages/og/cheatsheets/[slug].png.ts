import { getCollection } from 'astro:content';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

const WIDTH = 1200;
const HEIGHT = 630;

async function loadFont() {
  const response = await fetch(
    'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap'
  );
  const css = await response.text();
  
  const fontUrl = css.match(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/)?.[1];
  if (!fontUrl) throw new Error('Failed to extract font URL');
  
  const fontResponse = await fetch(fontUrl);
  return await fontResponse.arrayBuffer();
}

export async function getStaticPaths() {
  const cheatsheets = await getCollection('cheatsheets');
  
  return cheatsheets.map((cheatsheet) => ({
    params: { slug: cheatsheet.slug },
    props: { cheatsheet },
  }));
}

export async function GET({ props }: { props: { cheatsheet: any } }) {
  const { cheatsheet } = props;
  const { title, description } = cheatsheet.data;
  
  const fontData = await loadFont();
  
  const svg = await satori(
    {
      type: 'div',
      props: {
        style: {
          width: WIDTH,
          height: HEIGHT,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '64px',
          background: '#0d0d0d',
          fontFamily: 'Outfit',
        },
        children: [
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                flexDirection: 'column',
                gap: '24px',
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
                            background: '#6ee7b7',
                            borderRadius: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '28px',
                            fontWeight: 700,
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
                            fontWeight: 600,
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
                      gap: '12px',
                      marginTop: '32px',
                    },
                    children: [
                      {
                        type: 'div',
                        props: {
                          style: {
                            padding: '8px 16px',
                            background: 'rgba(110, 231, 183, 0.1)',
                            border: '1px solid #6ee7b7',
                            borderRadius: '4px',
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#6ee7b7',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          },
                          children: 'Cheat Sheet',
                        },
                      },
                    ],
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '72px',
                      fontWeight: 700,
                      color: '#e8e8e8',
                      lineHeight: 1.1,
                      maxWidth: '1000px',
                      marginTop: '24px',
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
                      marginTop: '16px',
                    },
                    children: description || 'Quick reference guide for developers',
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
                justifyContent: 'space-between',
                marginTop: '48px',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '20px',
                      fontWeight: 400,
                      color: '#8a8a8a',
                    },
                    children: 'devnook.dev',
                  },
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      display: 'flex',
                      gap: '8px',
                      alignItems: 'center',
                    },
                    children: [
                      {
                        type: 'div',
                        props: {
                          style: {
                            width: '8px',
                            height: '8px',
                            background: '#6ee7b7',
                            borderRadius: '50%',
                          },
                        },
                      },
                      {
                        type: 'div',
                        props: {
                          style: {
                            fontSize: '18px',
                            fontWeight: 400,
                            color: '#8a8a8a',
                          },
                          children: 'Developer Resources',
                        },
                      },
                    ],
                  },
                },
              ],
            },
          },
        ],
      },
    },
    {
      width: WIDTH,
      height: HEIGHT,
      fonts: [
        {
          name: 'Outfit',
          data: fontData,
          weight: 400,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: fontData,
          weight: 600,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: fontData,
          weight: 700,
          style: 'normal',
        },
      ],
    }
  );
  
  const resvg = new Resvg(svg, {
    fitTo: {
      mode: 'width',
      value: WIDTH,
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
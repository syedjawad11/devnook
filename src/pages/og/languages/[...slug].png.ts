import { getCollection } from 'astro:content';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

export async function getStaticPaths() {
  const languagePosts = await getCollection('languages');
  
  return languagePosts.map((entry) => ({
    params: { 
      slug: `${entry.data.language}/${entry.data.concept}`
    },
    props: { entry }
  }));
}

export async function GET({ props }: any) {
  const { entry } = props;
  
  const outfitRegular = await fetch(
    'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap'
  ).then((res) => res.text());
  
  const outfitUrl = outfitRegular.match(/url\((https:\/\/[^)]+\.woff2)\)/)?.[1];
  
  const outfitFont = outfitUrl 
    ? await fetch(outfitUrl).then((res) => res.arrayBuffer())
    : null;

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
          fontFamily: 'Outfit, sans-serif',
          position: 'relative'
        },
        children: [
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                marginBottom: '48px'
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
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '28px',
                      fontWeight: 700,
                      color: '#0d0d0d'
                    },
                    children: 'DN'
                  }
                },
                {
                  type: 'div',
                  props: {
                    style: {
                      fontSize: '32px',
                      fontWeight: 600,
                      color: '#e8e8e8'
                    },
                    children: 'DevNook'
                  }
                }
              ]
            }
          },
          {
            type: 'div',
            props: {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '24px'
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      backgroundColor: '#6ee7b7',
                      color: '#0d0d0d',
                      fontSize: '18px',
                      fontWeight: 600,
                      padding: '8px 16px',
                      borderRadius: '6px',
                      textTransform: 'uppercase'
                    },
                    children: entry.data.language
                  }
                }
              ]
            }
          },
          {
            type: 'div',
            props: {
              style: {
                fontSize: '64px',
                fontWeight: 700,
                color: '#e8e8e8',
                lineHeight: 1.1,
                marginBottom: '24px',
                maxWidth: '1000px'
              },
              children: entry.data.title
            }
          },
          {
            type: 'div',
            props: {
              style: {
                fontSize: '28px',
                color: '#8a8a8a',
                lineHeight: 1.4,
                maxWidth: '900px'
              },
              children: entry.data.description
            }
          }
        ]
      }
    },
    {
      width: 1200,
      height: 630,
      fonts: outfitFont ? [
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 400,
          style: 'normal'
        },
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 600,
          style: 'normal'
        },
        {
          name: 'Outfit',
          data: outfitFont,
          weight: 700,
          style: 'normal'
        }
      ] : []
    }
  );

  const resvg = new Resvg(svg, {
    fitTo: {
      mode: 'width',
      value: 1200
    }
  });

  const png = resvg.render().asPng();

  return new Response(png, {
    headers: {
      'Content-Type': 'image/png',
      'Cache-Control': 'public, max-age=31536000, immutable'
    }
  });
}
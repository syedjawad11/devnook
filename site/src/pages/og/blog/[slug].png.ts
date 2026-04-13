import { getCollection } from 'astro:content';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

export async function getStaticPaths() {
  const blogPosts = await getCollection('blog');
  
  return blogPosts.map((post) => ({
    params: { slug: post.slug },
    props: { post }
  }));
}

export async function GET({ props }: { props: any }) {
  const { post } = props;
  
  const outfitRegular = await fetch(
    'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap'
  ).then((res) => res.text());
  
  const outfitRegularUrl = outfitRegular.match(/src: url\((.+?)\)/)?.[1];
  
  if (!outfitRegularUrl) {
    throw new Error('Failed to load Outfit font');
  }
  
  const outfitRegularData = await fetch(outfitRegularUrl).then((res) => res.arrayBuffer());
  
  const outfitBold = await fetch(
    'https://fonts.googleapis.com/css2?family=Outfit:wght@700&display=swap'
  ).then((res) => res.text());
  
  const outfitBoldUrl = outfitBold.match(/src: url\((.+?)\)/)?.[1];
  
  if (!outfitBoldUrl) {
    throw new Error('Failed to load Outfit Bold font');
  }
  
  const outfitBoldData = await fetch(outfitBoldUrl).then((res) => res.arrayBuffer());
  
  const title = post.data.title;
  const description = post.data.description;
  const category = post.data.category;
  
  const svg = await satori(
    {
      type: 'div',
      props: {
        style: {
          display: 'flex',
          flexDirection: 'column',
          width: '1200px',
          height: '630px',
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
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                    },
                    children: [
                      {
                        type: 'div',
                        props: {
                          style: {
                            width: '40px',
                            height: '40px',
                            borderRadius: '8px',
                            backgroundColor: '#6ee7b7',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          },
                          children: [
                            {
                              type: 'div',
                              props: {
                                style: {
                                  color: '#0d0d0d',
                                  fontSize: '24px',
                                  fontWeight: 700,
                                },
                                children: 'D',
                              },
                            },
                          ],
                        },
                      },
                      {
                        type: 'div',
                        props: {
                          style: {
                            color: '#e8e8e8',
                            fontSize: '28px',
                            fontWeight: 700,
                          },
                          children: 'DevNook',
                        },
                      },
                    ],
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
                marginBottom: '24px',
              },
              children: [
                {
                  type: 'div',
                  props: {
                    style: {
                      backgroundColor: '#6ee7b7',
                      color: '#0d0d0d',
                      padding: '8px 16px',
                      borderRadius: '8px',
                      fontSize: '18px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    },
                    children: category,
                  },
                },
              ],
            },
          },
          {
            type: 'div',
            props: {
              style: {
                color: '#e8e8e8',
                fontSize: title.length > 60 ? '52px' : '64px',
                fontWeight: 700,
                lineHeight: 1.2,
                marginBottom: '24px',
                display: 'flex',
                flexWrap: 'wrap',
              },
              children: title,
            },
          },
          {
            type: 'div',
            props: {
              style: {
                color: '#8a8a8a',
                fontSize: '28px',
                fontWeight: 400,
                lineHeight: 1.4,
                display: 'flex',
                flexWrap: 'wrap',
              },
              children: description.length > 120 ? description.slice(0, 120) + '...' : description,
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
          data: outfitRegularData,
          weight: 400,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: outfitRegularData,
          weight: 600,
          style: 'normal',
        },
        {
          name: 'Outfit',
          data: outfitBoldData,
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
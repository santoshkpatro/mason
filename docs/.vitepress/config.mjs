import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Mason — The Python Web Framework",
  description: "A convention-first MVC framework for building fast, structured Python web apps.",
  cleanUrls: true,

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Examples', link: '/examples/controller' },
    ],

    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Getting Started', link: '/guide/getting-started' },
          { text: 'Routing', link: '/guide/routing' },
          { text: 'Controllers', link: '/guide/controllers' },
          { text: 'Models', link: '/guide/models' },
          { text: 'Templates', link: '/guide/templates' },
        ],
      },
      {
        text: 'Examples',
        items: [
          { text: 'Controller Example', link: '/examples/controller' },
          { text: 'Service Example', link: '/examples/service' },
        ]
      },
      {
        text: 'Reference',
        items: [
          { text: 'CLI Commands', link: '/reference/cli' },
          { text: 'Configuration', link: '/reference/config' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/santoshkpatro/mason' },
      { icon: 'email', link: 'mailto:hey@santoshkpatro.in' },
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: '© 2025 Santosh Kumar Patro'
    }
  }
})

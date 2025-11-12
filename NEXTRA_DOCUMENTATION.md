# Nextra Documentation Implementation

## Overview

The D3P documentation is now powered by **Nextra**, a Next.js-based documentation framework that integrates seamlessly with the existing application architecture.

## Why Nextra?

- **Native Next.js Integration**: No separate build process or authentication layer needed
- **Automatic Authentication**: Protected by existing Next.js middleware
- **No iframe issues**: Documentation is rendered as native Next.js pages
- **MDX Support**: Write documentation in Markdown with React components
- **Full-text Search**: Built-in search functionality
- **Responsive**: Mobile-friendly out of the box

## File Structure

```
frontend/
├── src/
│   ├── pages/
│   │   └── docs/
│   │       ├── _meta.json           # Sidebar navigation config
│   │       ├── index.mdx            # Getting Started page
│   │       ├── user-guides.mdx      # User guides
│   │       ├── api-reference.mdx    # API documentation
│   │       └── best-practices.mdx   # Best practices
│   └── menu-items/
│       └── documentation.tsx        # Menu integration
├── theme.config.tsx                 # Nextra theme configuration
└── next.config.js                   # Next.js config with Nextra
```

## How It Works

### Authentication

Documentation is automatically protected by the existing Next.js middleware (`src/middleware.ts`). The middleware applies to all routes, including `/docs`, ensuring only authenticated users can access documentation.

### Navigation

1. Users click "Documentation" in the app sidebar
2. Routes to `/docs` (a Next.js page)
3. Middleware checks authentication
4. If authenticated, renders Nextra documentation pages
5. If not, redirects to `/login`

### Theme Configuration

The `theme.config.tsx` file customizes the Nextra appearance:
- D3P branding
- Custom navbar with "Back to App" and "Logout" buttons
- Blue primary color matching D3P theme
- Disabled edit links (docs managed via git)
- Custom footer

## Adding Documentation

### Creating New Pages

1. Create a new `.mdx` file in `src/pages/docs/`:
   ```mdx
   # Page Title
   
   Your content here...
   ```

2. Add it to `_meta.json`:
   ```json
   {
     "index": "Getting Started",
     "new-page": "New Page Title"
   }
   ```

### Organizing with Folders

Create subdirectories for organized content:

```
src/pages/docs/
├── _meta.json
├── index.mdx
└── guides/
    ├── _meta.json
    ├── uploading.mdx
    └── reporting.mdx
```

`guides/_meta.json`:
```json
{
  "uploading": "Uploading Projects",
  "reporting": "Creating Reports"
}
```

## MDX Features

Nextra uses MDX, allowing React components in markdown:

```mdx
# My Page

Regular markdown content...

<Callout type="warning">
  Important note!
</Callout>

<Tabs items={['Tab 1', 'Tab 2']}>
  <Tab>Content 1</Tab>
  <Tab>Content 2</Tab>
</Tabs>
```

### Available Components

- `<Callout>` - Info boxes
- `<Tabs>` - Tabbed content
- `<Steps>` - Numbered steps
- `<Cards>` - Card layouts
- Any custom React component

## Local Development

```bash
cd frontend
npm run dev
```

Navigate to http://localhost:8081/docs

Changes to `.mdx` files hot-reload automatically!

## Deployment

Documentation is built as part of the regular Next.js build:

```bash
npm run build
```

No separate documentation build step needed - Nextra content is compiled with Next.js.

## Theme Customization

### Colors

Edit `theme.config.tsx`:
```typescript
primaryHue: 210, // 0-360, controls the primary color
```

### Navbar

Custom buttons are already configured in `theme.config.tsx`:
- Back to App button
- Logout button with Supabase integration

### Logo

Replace the logo in `theme.config.tsx`:
```typescript
logo: (
  <img src="/path/to/logo.png" alt="D3P" />
)
```

## Search

Nextra includes built-in full-text search. No configuration needed!

Press `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux) to open search.

## For Superadmins: Editing Documentation

### Via Git (Recommended)

1. Navigate to `frontend/src/pages/docs/`
2. Edit `.mdx` files
3. Commit changes
4. Push to repository
5. Deploy (documentation is included in normal deployment)

### File Naming

- Use lowercase with hyphens: `user-guides.mdx`
- Use `.mdx` extension for all documentation files
- Use `_meta.json` for navigation configuration

### Best Practices

1. **Keep it simple**: Use standard markdown for most content
2. **Add frontmatter**: Optional but useful for metadata
   ```mdx
   ---
   title: Page Title
   description: Page description for SEO
   ---
   ```
3. **Use callouts**: Highlight important information
4. **Link internally**: Use relative links between pages
   ```mdx
   See [User Guides](./user-guides) for more info.
   ```

## Troubleshooting

### Documentation not showing

- Check that the file is in `src/pages/docs/`
- Verify it's listed in `_meta.json`
- Restart dev server: `npm run dev`

### Styling looks wrong

- Clear `.next` cache: `rm -rf .next && npm run dev`
- Check `theme.config.tsx` for theme settings

### Links not working

- Use relative paths: `./other-page` not `/docs/other-page`
- Nextra handles routing automatically

## Resources

- [Nextra Documentation](https://nextra.site)
- [MDX Documentation](https://mdxjs.com)
- [Next.js Documentation](https://nextjs.org/docs)

## Migration Notes

### From Docusaurus

This replaces the previous Docusaurus implementation with several advantages:
- ✅ No separate build process
- ✅ No iframe complications
- ✅ Native authentication integration
- ✅ Hot reloading in development
- ✅ Simpler deployment
- ✅ Better performance

### Breaking Changes

- Documentation URL remains `/docs` (no change)
- All links work as expected (no iframe issues)
- Authentication automatically handled (no separate layer)

## Summary

Nextra provides a clean, integrated documentation solution that works seamlessly with D3P's existing Next.js architecture. Users can access documentation at `/docs`, and superadmins can edit content by modifying `.mdx` files in git.


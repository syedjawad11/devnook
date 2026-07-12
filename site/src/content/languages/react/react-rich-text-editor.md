---
title: "React Rich Text Editor: Top WYSIWYG Library Options"
description: "Learn which React rich text editor library fits your project: Tiptap, Lexical, Slate.js, and React-Quill compared with code examples and setup guidance."
category: "languages"
language: "react"
concept: "rich-text-editor"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, rich-text-editor, wysiwyg, tiptap, lexical]
related_posts: []
related_tools: []
linkAnchors:
  - "react rich text editor"
  - "react text editor"
  - "WYSIWYG editor React"
published_date: "2026-07-12"
og_image: "/og/languages/react/rich-text-editor.png"
word_count_target: 2012
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"React Rich Text Editor: Top WYSIWYG Library Options\",\"description\":\"Learn which React rich text editor library fits your project: Tiptap, Lexical, Slate.js, and React-Quill compared with code examples and setup guidance.\",\"datePublished\":\"2026-07-12\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/react/rich-text-editor/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is the best React rich text editor library?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Tiptap is the default choice — headless, extensible, and actively maintained. Its StarterKit covers standard formatting with a single import. Lexical by Meta is stronger when bundle size and rendering performance are constraints.\"}},{\"@type\":\"Question\",\"name\":\"Is Draft.js still a viable option?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Draft.js was moved to maintenance mode by Meta in 2024. New projects should use Tiptap, Lexical, or Slate.js instead — all are actively maintained.\"}},{\"@type\":\"Question\",\"name\":\"How do I integrate a React rich text editor with a form?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Wrap the editor with React Hook Form's Controller component. Connect the editor's onChange output to field.onChange and React Hook Form handles field registration. On submit, the field value is the HTML string the editor produced.\"}}]}\n</script>"
---
You are building a content management tool, a blogging platform, or a feedback form that needs more than plain text. Users expect bold, italic, bullet lists, and clickable links. A plain `<textarea>` gives you raw text. A bare `contenteditable` div is a browser compatibility nightmare. What you need is a react text editor — a component that manages rich document state, serializes it to HTML or JSON, and gives you a toolbar to drive it.

This guide compares four libraries — Tiptap, Lexical, Slate.js, and React-Quill — with working code so you can pick the right one for your project.

## React Rich Text Editor Libraries: What They Actually Do

A react rich text editor is a React component that sits on top of either ProseMirror, a custom document model, or a Quill.js core. At the library level it manages four things:

- a **document tree**: nodes (paragraphs, headings, lists) and marks (bold, italic, links)
- **cursor and selection state** across the editable region
- **undo/redo history**
- **serialization**: converting the document tree to HTML or JSON for storage

Each library makes different trade-offs between "works out of the box" and "customize everything." The comparison table below gives the overview before diving into the code:

| Library | Underlying engine | Bundle (approx.) | Headless? | Maintenance |
|---------|------------------|--------------------|-----------|-------------|
| Tiptap | ProseMirror | ~40 KB min | Yes | Active |
| Lexical | Custom (Meta) | ~22 KB min | Yes | Active |
| Slate.js | Custom | ~35 KB min | Yes | Active |
| React-Quill | Quill.js | ~50 KB min | No | Moderate |

---

## Setting Up Tiptap: The Go-To React Text Editor

[Tiptap](https://tiptap.dev) is the most widely used react rich text editor library. It wraps ProseMirror in an extension system and provides a clean React adapter. The result is a library that covers most formatting requirements without you touching the ProseMirror API directly.

Install the packages:

```bash
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit
```

Minimal working editor:

```jsx
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

export function RichTextEditor({ onChange }) {
  const editor = useEditor({
    extensions: [StarterKit],
    onUpdate({ editor }) {
      onChange(editor.getHTML())
    },
  })

  return <EditorContent editor={editor} />
}
```

`StarterKit` bundles bold, italic, strikethrough, headings (h1–h6), bullet lists, ordered lists, blockquotes, inline code, code blocks, horizontal rules, and undo/redo history — all from a single import. The `onUpdate` callback fires on every change. `editor.getHTML()` returns the current document as an HTML string; `editor.getJSON()` returns a structured ProseMirror document object.

Pick one output format and stay consistent in your database. Mixing HTML and JSON storage leads to import errors when you try to reload old content.

**Important:** `useEditor` is not a fully controlled React component. Do not feed a state-derived `content` prop back into the editor on every render — it resets the cursor position each time. Initialize once, then read output via `onUpdate`.

## Adding a Toolbar to Your React Rich Text Editor

Tiptap exposes `editor.chain()` for composing formatting commands:

```jsx
function Toolbar({ editor }) {
  if (!editor) return null
  return (
    <div style={{ display: 'flex', gap: '6px', marginBottom: '8px' }}>
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        style={{ fontWeight: editor.isActive('bold') ? 'bold' : 'normal' }}
      >B</button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        style={{ fontStyle: editor.isActive('italic') ? 'italic' : 'normal' }}
      >I</button>
      <button onClick={() => editor.chain().focus().toggleBulletList().run()}>
        • List
      </button>
      <button onClick={() => editor.chain().focus().setHeading({ level: 2 }).run()}>
        H2
      </button>
    </div>
  )
}

export function RichTextEditor({ onChange }) {
  const editor = useEditor({
    extensions: [StarterKit],
    onUpdate({ editor }) {
      onChange(editor.getHTML())
    },
  })

  return (
    <>
      <Toolbar editor={editor} />
      <EditorContent editor={editor} />
    </>
  )
}
```

`editor.chain().focus()` returns a command builder. Calling `.toggleBold().run()` at the end executes it. `editor.isActive('bold')` reads the current selection state so you can reflect active formats in your toolbar buttons. Every formatting command follows this same pattern — the method name changes, the structure stays identical.

## Lexical: Meta's Lightweight Alternative

[Lexical](https://lexical.dev) is Meta's replacement for Draft.js, first released in 2022. Instead of wrapping ProseMirror, it uses a custom node-graph model with a React reconciler. The result is a smaller core bundle and a more granular plugin system where each feature is an opt-in plugin.

```bash
npm install lexical @lexical/react
```

```jsx
import { LexicalComposer } from '@lexical/react/LexicalComposer'
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin'
import { ContentEditable } from '@lexical/react/LexicalContentEditable'
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin'
import { OnChangePlugin } from '@lexical/react/LexicalOnChangePlugin'

const editorConfig = {
  namespace: 'BlogEditor',
  onError(error) { throw error },
}

export function LexicalEditor({ onChange }) {
  return (
    <LexicalComposer initialConfig={editorConfig}>
      <RichTextPlugin
        contentEditable={<ContentEditable />}
        placeholder={<span>Write something...</span>}
        ErrorBoundary={({ children }) => children}
      />
      <HistoryPlugin />
      <OnChangePlugin onChange={onChange} />
    </LexicalComposer>
  )
}
```

Each feature — history, rich text, links, markdown shortcuts — is a separate plugin you import and drop inside `LexicalComposer`. This is more initial setup than Tiptap's `StarterKit`, but means you only ship the functionality your editor actually needs.

Lexical is the right choice when you need a smaller bundle for a performance-sensitive application, plan to build custom node types (embedded media blocks, interactive elements, collaborative cursors), or want fine-grained control over every aspect of the editor model.

## Slate.js: Maximum Customization

[Slate.js](https://docs.slatejs.org) takes a "bring your own everything" stance. It provides a plugin-based foundation but ships almost no default behaviors: no bold command, no keyboard shortcuts, no toolbar. Every behavior is authored by the developer.

```bash
npm install slate slate-react slate-history
```

```jsx
import { useState } from 'react'
import { createEditor } from 'slate'
import { Slate, Editable, withReact } from 'slate-react'
import { withHistory } from 'slate-history'

const initialValue = [
  { type: 'paragraph', children: [{ text: '' }] },
]

export function SlateEditor() {
  const [editor] = useState(() => withHistory(withReact(createEditor())))
  const [value, setValue] = useState(initialValue)

  return (
    <Slate editor={editor} initialValue={value} onChange={setValue}>
      <Editable placeholder="Start writing..." />
    </Slate>
  )
}
```

To add bold formatting you handle `onKeyDown` for Cmd+B yourself, write a `toggleMark` helper, and render marks through a custom `renderLeaf` prop. That is significantly more code than `StarterKit`. The trade-off is worth it when your product requires genuinely novel node types — embedded code playgrounds, interactive diagram blocks, or a structured form-builder embedded in prose. For a standard CMS editor with bold, italic, and lists, Slate is over-engineering.

## React-Quill: Fastest Drop-In

React-Quill wraps Quill.js and ships a styled toolbar without any configuration:

```bash
npm install react-quill
```

```jsx
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'

export function QuillEditor({ value, onChange }) {
  return <ReactQuill theme="snow" value={value} onChange={onChange} />
}
```

Two lines and you have a working editor with a visible formatting toolbar. The trade-offs: React-Quill has documented friction with React 18 concurrent rendering, and the project is less actively maintained than Tiptap or Lexical. It is a solid shortcut for internal tools, admin panels, and rapid prototypes. For production customer-facing editors, prefer Tiptap.

## Integrating a React Rich Text Editor with Forms

Rich text inputs are common inside forms. The cleanest integration pattern uses [React Hook Form's](/languages/react/hook-form/) `Controller` component to bridge the editor's `onChange` with form field registration:

```jsx
import { useForm, Controller } from 'react-hook-form'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

function TiptapField({ value, onChange }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: value,
    onUpdate({ editor }) {
      onChange(editor.getHTML())
    },
  })
  return <EditorContent editor={editor} />
}

export function ArticleForm() {
  const { control, handleSubmit } = useForm({
    defaultValues: { body: '' },
  })

  return (
    <form onSubmit={handleSubmit(data => console.log(data))}>
      <Controller
        name="body"
        control={control}
        render={({ field }) => (
          <TiptapField value={field.value} onChange={field.onChange} />
        )}
      />
      <button type="submit">Save Draft</button>
    </form>
  )
}
```

`Controller` handles field registration with React Hook Form. The editor's `onUpdate` fires `field.onChange`, which keeps React Hook Form's internal state current. On submit, `data.body` contains the HTML string your editor produced.

You can inspect and validate the HTML output your editor produces using the [HTML Formatter](/tools/html-formatter/) — useful during development to confirm the markup is well-formed before it reaches your database.

## Common Gotchas with React Rich Text Editors

**SSR hydration errors.** Rich text editors depend on browser APIs (`document`, `window`, `selection`). In Next.js, load them client-side only:

```jsx
import dynamic from 'next/dynamic'
const RichTextEditor = dynamic(() => import('./RichTextEditor'), { ssr: false })
```

Skipping this causes "window is not defined" at build time or hydration mismatches at runtime.

**Cursor reset on re-render.** Tiptap and Lexical are not fully controlled components. Avoid feeding a state-derived `content` prop back into the editor on each render — the editor resets cursor position on every update cycle. Initialize with content once; use `onUpdate` to read output.

**Stale form submission.** Reading `editor.getHTML()` inside `handleSubmit` rather than keeping state updated via `onUpdate` risks submitting outdated content when the user has typed but the React cycle has not completed. Always pipe output through `onUpdate` as shown in the form example above.

**Output format mismatch across library versions.** Storing HTML from one editor version and loading it into a newer one can produce rendering differences. For long-lived content, storing the Tiptap JSON schema alongside the HTML gives you a migration path when upgrading.

## Which React Text Editor Library Should You Pick?

Three questions guide the decision:

1. **Do you need a styled toolbar quickly?** → React-Quill for internal tools; Tiptap with a custom toolbar for customer-facing editors.
2. **Is bundle size critical?** → Lexical at ~22 KB wins.
3. **Do you need custom document node types?** → Slate.js.

For most teams building content editors, blog platforms, or CMS tools — Tiptap is the practical default. Its `StarterKit` covers 90% of requirements, the extension ecosystem is broad, and the [React components](/languages/react/components/) model maps cleanly onto Tiptap's component-based architecture.

## Frequently Asked Questions

### What is the best React rich text editor library?

Tiptap is the default choice for most product teams — headless, extensible, actively maintained, and the `StarterKit` covers standard formatting with a single import. Lexical by Meta is stronger when bundle size and rendering performance are constraints. React-Quill suits projects that need a styled editor running in minutes with no toolbar code.

### Is Draft.js still a viable option?

Draft.js was moved to maintenance mode by Meta in 2024. It still works in existing apps but receives no new features. Meta's own replacement is Lexical. New projects should use Tiptap, Lexical, or Slate.js.

### How do I integrate a React rich text editor with a form library?

Wrap the editor with [React Hook Form's](/languages/react/hook-form/) `Controller` component. Connect the editor's `onChange` output to `field.onChange`, and React Hook Form handles field registration. On form submit, the field value is the HTML or JSON string the editor produced.

### Can I use Tiptap with server-side rendering in Next.js?

Yes, but the editor must load client-side only. Use `dynamic(() => import('./YourEditor'), { ssr: false })` in Next.js. The editor relies on browser APIs not available during server rendering.

### What output format should I store from a React rich text editor?

HTML (`editor.getHTML()`) renders directly in any browser and is simple to work with. JSON (`editor.getJSON()`) preserves semantic document structure and is easier to migrate between editor library versions. For production apps with content that needs to outlast the library, JSON is the more future-proof choice.

## Conclusion

Choosing the right react rich text editor depends on how much configuration overhead you can absorb, how much you need to customize, and how sensitive your app is to bundle size. Tiptap is the practical default for most teams — its extension system handles the full react text editor feature set with minimal setup. Lexical is the better pick when performance and bundle constraints apply. Slate.js fits genuinely novel editor requirements. React-Quill is the fastest path to a working editor for internal tooling.

All four libraries are React components at their core — they accept props, fire events, and compose alongside the [React components](/languages/react/components/) you are already building. For form validation workflows, pair any editor with [React Hook Form](/languages/react/hook-form/) using the `Controller` pattern shown in this guide.

To see how React's rendering model applies beyond UI components, explore [React Lists and Rendering](/languages/react/lists-rendering/) — the same key-based reconciliation React uses for list items also governs how Tiptap updates its rendered node tree.

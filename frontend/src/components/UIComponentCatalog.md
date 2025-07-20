# UI Component Catalog & Usage Plan

This document catalogs all available UI components in `/components/ui` and outlines how they will be composed to build the main features of the SDR Trainer frontend. **Only these UI components will be used.**

---

## **Available UI Components**

- Accordion
- Alert
- AlertDialog
- AspectRatio
- Avatar
- Badge
- Breadcrumb
- Button
- Calendar
- Card
- Carousel
- Chart
- Checkbox
- Collapsible
- Command
- ContextMenu
- Dialog
- Drawer
- DropdownMenu
- Form
- HoverCard
- Input
- InputOtp
- Label
- Menubar
- NavigationMenu
- Pagination
- Popover
- Progress
- RadioGroup
- Resizable
- ScrollArea
- Select
- Separator
- Sheet
- Sidebar
- Skeleton
- Slider
- Sonner
- Switch
- Table
- Tabs
- Textarea
- Toggle
- ToggleGroup
- Tooltip

---

## **Feature Composition Plan**

### 1. **Dashboard / Session List**
- **Card**: Each session summary (title, score, date)
- **List/Table**: For displaying multiple sessions
- **Button**: For actions (start new session, view session)
- **Badge**: For score/status
- **Pagination**: If many sessions
- **Skeleton**: For loading state
- **NavigationMenu/Sidebar**: For app navigation

### 2. **Session Detail / Replay**
- **Card**: Container for session details
- **Tabs**: Switch between Conversation, Feedback, Analytics
- **List/Table**: Conversation turns (user/AI)
- **Avatar**: User/AI icons
- **Badge**: For persona/offer
- **Progress/Chart**: For score visualization
- **Button**: Replay audio, go back
- **Popover/Tooltip**: For extra info on feedback points
- **Separator**: Between conversation turns

### 3. **Live Call UI**
- **Form/Input/Textarea**: Persona/offer input
- **Button**: Start/stop call, send
- **Card**: Main call UI container
- **Progress**: Audio recording/streaming status
- **Tabs**: Switch between transcript and AI response
- **Alert**: For errors or session end
- **Slider**: For volume control (if needed)
- **Switch**: Toggle features (e.g., TTS on/off)

### 4. **Feedback Display**
- **List**: Bullet points for feedback
- **Badge**: Highlight key feedback
- **Popover/Tooltip**: Explain feedback points
- **Alert**: For important feedback

### 5. **General Layout & Navigation**
- **Sidebar/NavigationMenu**: Main app navigation
- **Drawer/Sheet**: Mobile navigation or settings
- **Breadcrumb**: For navigation context
- **Tabs**: For switching between app sections

---

## **Component Composition Examples**

- **SessionList**: Card + List + Badge + Button
- **SessionDetail**: Card + Tabs + List + Avatar + Badge + Progress + Button
- **LiveCall**: Card + Form + Input + Button + Progress + Tabs + Alert
- **FeedbackPoints**: List + Badge + Popover

---

**All components will use only classes and variables from `globals.css` for styling.** 
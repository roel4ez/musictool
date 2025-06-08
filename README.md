# MusicTool

This repository aims to create a music management tool for personal use. The main source of music will be from the Traktor Pro 3 library, which will be used to manage and organize a music collection. In the future, the tool will also allow for the import of music from other sources, such as Bandcamp, and will provide a way to manage and organize that music as well.

## Features

- Show list of music files, including metadata
- Join metadata with data from Discogs, currently available in a local database
- Allow to lookup metadata from Discogs
- Allow to edit metadata
- Allow to lookup availability of music on Bandcamp or Beatport

See [Project Description](docs/project-description.md) for more details.

## Development Setup

### Prerequisites

- Node.js (v16 or later)
- npm or yarn

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MusicTool.git
   cd MusicTool
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn
   ```

3. Build the TypeScript code:
   ```
   npm run build
   ```
   or
   ```
   yarn build
   ```

4. Start the application:
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

### Development Mode

To run the application in development mode with DevTools enabled:

```
npm run dev
```
or
```
yarn dev
```

## Building for Distribution

To package the application for distribution:

```
npm run dist
```
or
```
yarn dist
```

This will create installers for your platform in the `release` directory.

## Project Structure

- `/src` - Source code
  - `/components` - React components
  - `/utils` - Utility functions including NML parser
  - `/types` - TypeScript type definitions
- `/assets` - Static assets (icons, etc.)
- `/dist` - Compiled JavaScript files
- `/release` - Distribution packages
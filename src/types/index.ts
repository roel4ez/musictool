export interface MusicFile {
  artist: string;
  title: string;
  label?: string;
  year?: string;
  genre?: string;
  album?: string;
  comment?: string;
  bpm?: number;
  duration?: string; // Track length in format MM:SS
  filePath: string;
  location?: FileLocation;
  info?: FileInfo;
  tempo?: Tempo;
  raw?: any; // For storing the original XML data
}

export interface FileLocation {
  dir: string;
  file: string;
  volume: string;
  volumeId: string;
}

export interface FileInfo {
  bitrate?: string;
  genre?: string;
  label?: string;
  comment?: string;
  key?: string;
  playCount?: number;
  playTime?: string;
  importDate?: string;
  lastPlayed?: string;
  releaseDate?: string;
  fileSize?: string;
}

export interface Tempo {
  bpm: number;
  bpmQuality: number;
}

export interface Album {
  title: string;
  track?: string;
}

export interface Settings {
  lastOpenedFile?: string;
  columnVisibility: {
    [key: string]: boolean;
  };
  defaultSortField: string;
  defaultSortDirection: 'asc' | 'desc';
}

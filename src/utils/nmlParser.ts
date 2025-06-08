import { promises as fs } from 'fs';
import { XMLParser } from 'fast-xml-parser';
import { MusicFile, FileLocation, FileInfo, Tempo, Album } from '../types';

// XML parsing options
const parserOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: '',
  isArray: (name: string) => {
    return ['ENTRY'].includes(name);
  }
};

/**
 * Parse Traktor NML file and extract music files with metadata
 */
export async function parseNMLFile(filePath: string): Promise<MusicFile[]> {
  try {
    // Read the NML file
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    // Parse XML to JSON
    const parser = new XMLParser(parserOptions);
    const result = parser.parse(fileContent);
    
    if (!result.NML?.COLLECTION?.ENTRY) {
      throw new Error('Invalid NML file structure');
    }
    
    // Extract music files
    const entries = result.NML.COLLECTION.ENTRY;
    
    return entries.map((entry: any): MusicFile => {
      // Extract location info
      const location: FileLocation = {
        dir: entry.LOCATION?.DIR || '',
        file: entry.LOCATION?.FILE || '',
        volume: entry.LOCATION?.VOLUME || '',
        volumeId: entry.LOCATION?.VOLUMEID || ''
      };
      
      // Extract file info
      const info: FileInfo = entry.INFO ? {
        bitrate: entry.INFO.BITRATE,
        genre: entry.INFO.GENRE,
        label: entry.INFO.LABEL,
        comment: entry.INFO.COMMENT,
        key: entry.INFO.KEY,
        playCount: parseInt(entry.INFO.PLAYCOUNT, 10) || 0,
        playTime: entry.INFO.PLAYTIME,
        importDate: entry.INFO.IMPORT_DATE,
        lastPlayed: entry.INFO.LAST_PLAYED,
        releaseDate: entry.INFO.RELEASE_DATE,
        fileSize: entry.INFO.FILESIZE
      } : {};
      
      // Extract tempo info
      const tempo: Tempo = entry.TEMPO ? {
        bpm: parseFloat(entry.TEMPO.BPM) || 0,
        bpmQuality: parseFloat(entry.TEMPO.BPM_QUALITY) || 0
      } : { bpm: 0, bpmQuality: 0 };
      
      // Extract album info
      const album: Album = entry.ALBUM ? {
        title: entry.ALBUM.TITLE || '',
        track: entry.ALBUM.TRACK
      } : { title: '' };
      
      // Format track duration (playtime in seconds to MM:SS)
      const duration = info.playTime ? formatDuration(parseInt(info.playTime, 10)) : '';
      
      // Create music file object
      return {
        artist: entry.ARTIST || '',
        title: entry.TITLE || '',
        label: info.label || '',
        year: info.releaseDate ? info.releaseDate.split('/')[0] : '',
        genre: info.genre || '',
        album: album.title || '',
        comment: info.comment || '',
        bpm: tempo.bpm || 0,
        duration,
        filePath: constructFilePath(location),
        location,
        info,
        tempo,
        raw: entry
      };
    });
    
  } catch (error) {
    console.error('Error parsing NML file:', error);
    throw error;
  }
}

/**
 * Format duration from seconds to MM:SS
 */
function formatDuration(seconds: number): string {
  if (!seconds) return '';
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Construct file path from location object
 */
function constructFilePath(location: FileLocation): string {
  if (!location.dir || !location.file) return '';
  
  // Convert Traktor path format to OS path
  const path = location.dir
    .replace(/^\/:/g, '')
    .replace(/\/:/g, '/')
    .replace(/\/$/, '');
    
  return `${path}/${location.file}`;
}

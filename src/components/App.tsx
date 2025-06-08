import React, { useState, useEffect } from 'react';
import { ChakraProvider, Box, Heading, Text, Button, useToast } from '@chakra-ui/react';
import { MusicFile } from '../types';
import { parseNMLFile } from '../utils/nmlParser';
import MusicFileTable from './MusicFileTable';

const App: React.FC = () => {
  const [musicFiles, setMusicFiles] = useState<MusicFile[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [filePath, setFilePath] = useState<string>('');
  const toast = useToast();

  // Listen for file open events from the main process
  useEffect(() => {
    // Set up IPC listeners
    window.api.receive('file-opened', handleFileOpen);
    
    return () => {
      // Clean up listeners
      // Note: In a real implementation we'd need to remove the listeners
    };
  }, []);

  // Handle file open event
  const handleFileOpen = async (path: string) => {
    setFilePath(path);
    await loadNMLFile(path);
  };

  // Load and parse NML file
  const loadNMLFile = async (path: string) => {
    try {
      setIsLoading(true);
      const files = await parseNMLFile(path);
      setMusicFiles(files);
      toast({
        title: 'File loaded',
        description: `Loaded ${files.length} tracks from library`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error loading NML file:', error);
      toast({
        title: 'Error',
        description: 'Failed to load NML file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Open file dialog
  const openFileDialog = () => {
    window.api.send('open-file-dialog');
  };

  return (
    <ChakraProvider>
      <Box p={5} height="100vh" display="flex" flexDirection="column">
        <Box mb={5}>
          <Heading as="h1" size="xl" mb={2}>MusicTool</Heading>
          <Text fontSize="md" color="gray.500">
            {filePath ? `Current file: ${filePath}` : 'No file loaded'}
          </Text>
          <Button 
            mt={3} 
            colorScheme="blue" 
            onClick={openFileDialog}
            isLoading={isLoading}
          >
            Open NML File
          </Button>
        </Box>
        
        <Box flex="1" overflow="auto">
          <MusicFileTable 
            musicFiles={musicFiles} 
            isLoading={isLoading} 
          />
        </Box>
      </Box>
    </ChakraProvider>
  );
};

export default App;

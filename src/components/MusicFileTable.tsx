import React, { useMemo } from 'react';
import { 
  Table, Thead, Tbody, Tr, Th, Td, 
  Box, Spinner, Text, useColorModeValue 
} from '@chakra-ui/react';
import { MusicFile } from '../types';

interface MusicFileTableProps {
  musicFiles: MusicFile[];
  isLoading: boolean;
}

const MusicFileTable: React.FC<MusicFileTableProps> = ({ 
  musicFiles, 
  isLoading 
}) => {
  // Column definitions
  const columns = useMemo(() => [
    { Header: 'Artist', accessor: 'artist' },
    { Header: 'Title', accessor: 'title' },
    { Header: 'Album', accessor: 'album' },
    { Header: 'Genre', accessor: 'genre' },
    { Header: 'Label', accessor: 'label' },
    { Header: 'Year', accessor: 'year' },
    { Header: 'BPM', accessor: 'bpm' },
    { Header: 'Duration', accessor: 'duration' },
    { Header: 'Comment', accessor: 'comment' },
    { Header: 'File Path', accessor: 'filePath' }
  ], []);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (musicFiles.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="400px"
        borderWidth="1px"
        borderRadius="lg"
        borderColor={borderColor}
      >
        <Text fontSize="lg" color="gray.500">
          No music files loaded. Please open an NML file.
        </Text>
      </Box>
    );
  }

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      overflow="hidden" 
      bg={bgColor}
      boxShadow="sm"
    >
      <Box overflowX="auto">
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              {columns.map((column) => (
                <Th key={column.accessor}>
                  {column.Header}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {musicFiles.map((file, index) => (
              <Tr key={index}>
                <Td>{file.artist}</Td>
                <Td>{file.title}</Td>
                <Td>{file.album}</Td>
                <Td>{file.genre}</Td>
                <Td>{file.label}</Td>
                <Td>{file.year}</Td>
                <Td>{file.bpm}</Td>
                <Td>{file.duration}</Td>
                <Td>{file.comment}</Td>
                <Td>{file.filePath}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
};

export default MusicFileTable;

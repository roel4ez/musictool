// Global interface extensions
interface Window {
  api: {
    receive: (channel: string, func: (...args: any[]) => void) => void;
    send: (channel: string, data?: any) => void;
  };
}

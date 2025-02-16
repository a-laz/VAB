declare module 'axios' {
    export interface AxiosError {
        message: string;
        response?: {
            data?: {
                message?: string;
            };
        };
    }

    const axios: {
        post: (url: string, data?: any, config?: any) => Promise<any>;
        // Add other methods as needed
    };

    export default axios;
} 
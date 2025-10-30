import axios from 'axios';
import {  createClient} from 'utils/supabase';
interface InviteUserProps {
    user_email: string
    company_id: string
}

const inviteUser = async ({ inviteProps }: {inviteProps: InviteUserProps}): Promise<string> => {
    const supabase = createClient();
    const { data: session } = await supabase.auth.getSession();
    try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/invite_user/`, {
            ...inviteProps
        },
        {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session?.session?.access_token}`
            }
        });
        
        if (response.data === 'success') {
            return 'success';
        }
        else {
            return 'failed';
        }
    } catch (error) {
        console.error('Error creating project:', error);
        // Log additional error details
        if (axios.isAxiosError(error)) {
            console.error('Axios error response:', error.response);
            if (error.response?.status !== 200) {
                return error.response?.data?.detail ?? `Unknown error`;
            }
            return `Axios error: ${error.message}`;
        }
        const errorMessage = (error as Error).message;
        return `Unexpected error: ${errorMessage}`;
    }
};

export default inviteUser;
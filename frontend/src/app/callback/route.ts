import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest){
    const url = new URL(req.url)

    console.log('=== CALLBACK ROUTE DEBUG ===');
    console.log('URL:', url.href);
    console.log('Query params:', Object.fromEntries(url.searchParams));

    const code = url.searchParams.get('code')
    const error = url.searchParams.get('error')
    const errorCode = url.searchParams.get('error_code')
    const errorDescription = url.searchParams.get('error_description')

    // Check for errors from Supabase (expired links, etc.)
    if (error) {
        console.error('Auth callback error:', { error, errorCode, errorDescription });
        
        // Create user-friendly error message
        let message = errorDescription || error;
        
        // Customize message for common errors
        if (errorCode === 'otp_expired' || error === 'access_denied') {
            message = 'This magic link has expired or has already been used. Please request a new one by entering your email address below.';
        }
        
        const encodedMessage = encodeURIComponent(message);
        console.log('Redirecting to login with error:', message);
        
        // Use url.origin directly - we're already on the frontend
        return NextResponse.redirect(`${url.origin}/login?error=auth_failed&message=${encodedMessage}`);
    }

    if(code){
        console.log('Code found, attempting exchange...');
        const cookieStore = await cookies();

        const supabase = createRouteHandlerClient({
            cookies: () => cookieStore
        })
        
        try {
            const { data, error: exchangeError } = await supabase
                .auth
                .exchangeCodeForSession(code)
            
            console.log('Exchange result:', { 
                hasSession: !!data?.session, 
                hasError: !!exchangeError,
                errorMessage: exchangeError?.message 
            });
            
            if (exchangeError) {
                console.error('Error exchanging code for session:', exchangeError);
                const message = encodeURIComponent(exchangeError.message);
                return NextResponse.redirect(`${url.origin}/login?error=auth_failed&message=${message}`);
            }
            
            if (data?.session) {
                console.log('✓ Successfully authenticated:', data.session.user.email);
                return NextResponse.redirect(`${url.origin}/dashboard/default`);
            } else {
                console.error('No session returned from exchange');
                return NextResponse.redirect(`${url.origin}/login?error=auth_failed&message=${encodeURIComponent('No session established from magic link')}`);
            }
        } catch (err) {
            console.error('Unexpected error during code exchange:', err);
            const message = encodeURIComponent((err as Error)?.message || 'Unexpected authentication error');
            return NextResponse.redirect(`${url.origin}/login?error=auth_failed&message=${message}`);
        }
    }

    // No code provided, redirect to login
    console.log('No code in URL, redirecting to login');
    return NextResponse.redirect(`${url.origin}/login`)

}
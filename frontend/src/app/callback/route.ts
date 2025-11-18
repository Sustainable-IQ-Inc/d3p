import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest){
    const url = new URL(req.url)

    // Get the correct origin from headers (Cloud Run uses X-Forwarded-Host)
    const forwardedHost = req.headers.get('x-forwarded-host');
    const forwardedProto = req.headers.get('x-forwarded-proto') || 'https';
    const correctOrigin = forwardedHost ? `${forwardedProto}://${forwardedHost}` : url.origin;

    const code = url.searchParams.get('code')
    const error = url.searchParams.get('error')
    const errorCode = url.searchParams.get('error_code')
    const errorDescription = url.searchParams.get('error_description')

    // Check for errors from Supabase (expired links, etc.)
    if (error) {
        // Create user-friendly error message
        let message = errorDescription || error;
        
        // Customize message for common errors
        if (errorCode === 'otp_expired' || error === 'access_denied') {
            message = 'This magic link has expired or has already been used. Please request a new one by entering your email address below.';
        }
        
        const encodedMessage = encodeURIComponent(message);
        return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${encodedMessage}`);
    }

    if(code){
        const cookieStore = await cookies();

        const supabase = createRouteHandlerClient({
            cookies: () => cookieStore
        })
        
        try {
            const { data, error: exchangeError } = await supabase
                .auth
                .exchangeCodeForSession(code)
            
            if (exchangeError) {
                console.error('Error exchanging code for session:', exchangeError);
                const message = encodeURIComponent(exchangeError.message);
                return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${message}`);
            }
            
            if (data?.session) {
                return NextResponse.redirect(`${correctOrigin}/dashboard/default`);
            } else {
                return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${encodeURIComponent('No session established from magic link')}`);
            }
        } catch (err) {
            console.error('Unexpected error during code exchange:', err);
            const message = encodeURIComponent((err as Error)?.message || 'Unexpected authentication error');
            return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${message}`);
        }
    }

    // No code provided, redirect to login
    return NextResponse.redirect(`${correctOrigin}/login`)

}
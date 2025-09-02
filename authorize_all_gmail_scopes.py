from langchain_arcade import ToolManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
arcade_api_key = os.environ.get('ARCADE_API_KEY')

# Initialize the tool manager
manager = ToolManager(api_key=arcade_api_key)
manager.init_tools(toolkits=['Gmail'])

print('🔍 Getting authorization URLs for ALL Gmail scopes...')

try:
    user_id = 'edangx3@gmail.com'
    print(f'👤 User ID: {user_id}')
    
    # Get all Gmail tools to identify different scopes needed
    tools = manager.to_langchain()
    gmail_tools = [tool.name for tool in tools if 'Gmail' in tool.name]
    
    print(f'📧 Found {len(gmail_tools)} Gmail tools:')
    for tool in gmail_tools:
        print(f'  - {tool}')
    
    # Try to authorize key tools that represent different scopes
    key_tools = ['Gmail_ListEmails', 'Gmail_WriteDraftEmail', 'Gmail_SendDraftEmail']
    authorization_urls = {}
    
    for tool_name in key_tools:
        try:
            print(f'\n🔧 Checking authorization status for: {tool_name}')
            
            # First check if the tool requires auth
            requires_auth = manager.requires_auth(tool_name)
            print(f'🔍 Requires auth: {requires_auth}')
            
            if not requires_auth:
                print(f'✅ {tool_name} does not require authorization')
                continue
            
            print(f'🔧 Attempting to authorize: {tool_name}')
            auth_response = manager.authorize(tool_name, user_id)
            
            # Check for authorization URL
            url = getattr(auth_response, 'url', None)
            status = getattr(auth_response, 'status', 'unknown')
            scopes = getattr(auth_response, 'scopes', [])
            
            print(f'📊 Status: {status}')
            
            if url:
                print(f'✅ SUCCESS! Authorization URL for {tool_name}:')
                print(f'🔗 {url}')
                print(f'🆔 Auth ID: {getattr(auth_response, "id", "unknown")}')
                print(f'📋 Scopes: {scopes}')
                
                authorization_urls[tool_name] = {
                    'url': url,
                    'scopes': scopes,
                    'id': getattr(auth_response, 'id', 'unknown')
                }
            elif status == 'completed':
                print(f'✅ Tool {tool_name} is already authorized!')
                if scopes:
                    print(f'📋 Active scopes: {", ".join(scopes)}')
            else:
                print(f'❌ Unexpected status for {tool_name}: {status}')
                
        except Exception as e:
            print(f'❌ Error with {tool_name}: {e}')
            import traceback
            traceback.print_exc()
            continue
    
    if authorization_urls:
        print(f'\n🎯 AUTHORIZATION SUMMARY:')
        print(f'Found {len(authorization_urls)} different authorization requirements:')
        
        for tool_name, auth_info in authorization_urls.items():
            print(f'\n📋 {tool_name}:')
            print(f'   Scopes: {", ".join(auth_info["scopes"])}')
            print(f'   URL: {auth_info["url"]}')
        
        print(f'\n🚀 NEXT STEPS:')
        print(f'You need to authorize each URL above to use all Gmail features.')
        print(f'Each URL represents different Gmail permissions:')
        print(f'- gmail.readonly: Read emails and search')
        print(f'- gmail.compose: Create and send emails')
        print(f'- gmail.modify: Modify emails (drafts, labels, etc.)')
        
        print(f'\n⭐ RECOMMENDED: Authorize ALL URLs above, then test arcade_3_agent_with_memory.py')
    else:
        print(f'\n🎉 EXCELLENT! All Gmail tools are already fully authorized!')
        print(f'✅ Your Gmail Assistant is ready to use!')
        print(f'')
        print(f'📧 Available Gmail scopes:')
        print(f'   • gmail.readonly - Read emails and search')
        print(f'   • gmail.compose - Create and edit drafts')  
        print(f'   • gmail.send - Send emails')
        print(f'')
        print(f'🚀 NEXT STEPS:')
        print(f'   1. Run the Streamlit app: streamlit run arcade_3_streamlit_app.py')
        print(f'   2. Or run the CLI: python gmail_cli_assistant.py')
        print(f'   3. Start asking questions like "Show me my recent emails"')
    
except Exception as e:
    print(f'❌ General error: {e}')

print('\n🏁 Authorization script completed.')
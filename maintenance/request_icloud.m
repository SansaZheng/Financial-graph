#import <Foundation/Foundation.h>
int main(int argc,const char**argv){@autoreleasepool{
 NSData *data=[NSData dataWithContentsOfFile:@"/Users/zyy/.local/share/financial-graph/maintenance/mac-data-manifest.json"];
 NSDictionary *manifest=[NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
 for(NSDictionary *entry in manifest[@"failed"]){
 NSString *path=entry[@"source"];NSURL *url=[NSURL fileURLWithPath:path];NSError *error=nil;
 BOOL ok=[[NSFileManager defaultManager] startDownloadingUbiquitousItemAtURL:url error:&error];
 NSDictionary *result=@{@"source":path,@"request_accepted":@(ok),@"error":error.localizedDescription?:@""};
 NSData *line=[NSJSONSerialization dataWithJSONObject:result options:0 error:nil];
 puts([[NSString alloc]initWithData:line encoding:NSUTF8StringEncoding].UTF8String);fflush(stdout);
 }
}return 0;}

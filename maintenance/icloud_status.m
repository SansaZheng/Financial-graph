#import <Foundation/Foundation.h>
int main(){@autoreleasepool{
NSDictionary *m=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@"/Users/zyy/.local/share/financial-graph/maintenance/mac-data-manifest.json"] options:0 error:nil];
for(NSDictionary *e in m[@"failed"]){NSURL *u=[NSURL fileURLWithPath:e[@"source"]];NSError *err=nil;NSDictionary *v=[u resourceValuesForKeys:@[NSURLIsUbiquitousItemKey,NSURLUbiquitousItemDownloadingStatusKey,NSURLUbiquitousItemIsDownloadingKey,NSURLUbiquitousItemDownloadingErrorKey] error:&err];
NSMutableDictionary *r=[NSMutableDictionary dictionaryWithDictionary:@{@"source":e[@"source"],@"error":err.localizedDescription?:@""}];for(NSString *key in v)r[key]=[v[key] description];NSData *d=[NSJSONSerialization dataWithJSONObject:r options:0 error:nil];puts([[NSString alloc]initWithData:d encoding:NSUTF8StringEncoding].UTF8String);}
}return 0;}

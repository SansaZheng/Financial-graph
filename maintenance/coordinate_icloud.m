#import <Foundation/Foundation.h>
int main(){@autoreleasepool{
NSDictionary *m=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@"/Users/zyy/.local/share/financial-graph/maintenance/mac-data-manifest.json"] options:0 error:nil];
NSString *path=m[@"failed"][0][@"source"];NSFileCoordinator *c=[[NSFileCoordinator alloc]initWithFilePresenter:nil];NSError *e=nil;
[c coordinateReadingItemAtURL:[NSURL fileURLWithPath:path] options:NSFileCoordinatorReadingWithoutChanges error:&e byAccessor:^(NSURL *u){NSError *readError=nil;NSData *d=[NSData dataWithContentsOfURL:u options:0 error:&readError];printf("coordinated_read_bytes=%lu error=%s\n",(unsigned long)d.length,(readError.localizedDescription?:@"").UTF8String);fflush(stdout);}];
printf("coordination_error=%s\n",(e.localizedDescription?:@"").UTF8String);
}return 0;}

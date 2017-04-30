## Configuration for Jenkins

 * The option `Delete workspace before build starts` should be **unchecked**.  With it running, we are unable to get a reasonable time when Javadoc was last run.
 * There are three addition post-build tasks that need to be added (pictures below) and the normal post-build task will have to be recreated as the last task (since it must execute last).

----

 * Task 1: Failure of TS_Test Compilation

`Compile failed` AND `/ts_test/` as log text options

`echo "Y" > $WORKDIR/compLog.txt`

`echo "N" >> $WORKDIR/compLog.txt`

![alt text](ts_test_fail.png "Alt text; lorem ipsum")

   * Task 2: Failure of Student Source Code Compilation

`Compile failed` AND `/src/` as log text options

`echo "N" > $WORKDIR/compLog.txt`

`echo "N" >> $WORKDIR/compLog.txt`

![alt text](st_src_fail.png "Alt text; lorem ipsum")

   * Task 3: Failure of Student Test Compilation

`Compile failed` AND `/test/` as log text options

`echo "N" > $WORKDIR/compLog.txt`

`echo "N" >> $WORKDIR/compLog.txt`

![alt text](st_test_fail.png "Alt text; lorem ipsum")

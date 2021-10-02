use std::fs;
use std::fs::File;
use std::str;

use tokio::process::Command;

use crate::{CodeExecutionResult, CodeToExecute};

pub(crate) async fn execute_code(program: CodeToExecute) {
    let target_dir = "/programs/".to_string() + stringify!(program.id);
    fs::create_dir_all(&target_dir);

    let mut file = File::create(target_dir + "/submission.cpp");

    Command::new("isolate").arg("--cleanup");
    Command::new("isolate").arg("--init");


    // compile with: isolate --run -p --dir=/a=/var/www/a  -- /usr/bin/g++ /a/b.cpp -o out

    let output = Command::new("g++")
        .args(&[
            "--run",
            "-p",
            &("--dir=/code=/var/www/archibald/programs/".to_string() + stringify!(program.id)),
            "--",
            "/usr/bin/g++",
            "/code/submission.cpp",
            "-o",
            "out"])
        .output().await.expect("Compilation output");
    let compilation_stdout = match str::from_utf8(&output.stdout) {
        Ok(v) => v,
        Err(e) => "Invalid UTF-8 sequence"
    };
    let compilation_stderr = match str::from_utf8(&output.stderr) {
        Ok(v) => v,
        Err(e) => "Invalid UTF-8 sequence"
    };

    let run_output = Command::new("isolate").args(&["--run", "--", "out"]).output().await.expect("Run command output");
    let stdout = match str::from_utf8(&run_output.stdout) {
        Ok(v) => v,
        Err(e) => "Invalid UTF-8 sequence"
    };
    let stderr = match str::from_utf8(&run_output.stderr) {
        Ok(v) => v,
        Err(e) => "Invalid UTF-8 sequence"
    };

    let result = CodeExecutionResult {
        successful: output.status.success(),
        stdout: Box::from(stdout),
        stderr: Box::from(stderr),
        compilation_stdout: Box::from(compilation_stdout),
        compilation_stderr: Box::from(compilation_stderr),
    };
}


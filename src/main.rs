mod executor;

use serenity::{
    async_trait,
    model::{
        gateway::Ready,
        interactions::{
            application_command::{
                ApplicationCommand,
                ApplicationCommandOptionType,
            },
            Interaction,
            InteractionResponseType,
        },
    },
    prelude::*,
};
use tokio::sync::mpsc::{Sender, Receiver, channel};
use serenity::futures::Future;
use std::pin::Pin;
use std::task::Poll;
use serenity::model::channel::Message;

struct Handler;

#[derive(Clone)]
struct CodeExecutionResult {
    successful: bool,
    compilation_stdout: Box<str>,
    compilation_stderr: Box<str>,
    stdout: Box<str>,
    stderr: Box<str>
}

struct CodeToExecute {
    id: u64,
    code: Box<str>,
    stdin: Option<Box<str>>,
    oneshot_sender: tokio::sync::oneshot::Sender<CodeExecutionResult>
}


struct CodeQueueSender;

impl TypeMapKey for CodeQueueSender {
    type Value = Sender<CodeToExecute>;
}


#[command]
async fn exec(ctx: &Context, msg: &Message) -> CommandResult {
    let (one_sender, receiver) = tokio::sync::oneshot::channel::<CodeExecutionResult>();
    let source_code = &msg.content[6..];
    let mut new_program = CodeToExecute {
        id: u64::from(msg.id),
        code: Box::from(source_code),
        stdin: None,
        oneshot_sender: one_sender
    };

    {
        let data_read = ctx.data.read().await;
        let sender = data_read.get::<CodeQueueSender>().expect("Code queue sender").clone();
        sender.send(new_program);
    }

    let result = receiver.await.expect("code execution result");
    msg.reply(ctx, format!("{}{}", result.stdout, result.stderr)).await?;

    Ok(())
}

#[async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);

        let commands;
        if false {
            commands = ApplicationCommand::set_global_application_commands(&ctx.http, |commands| {
                commands
                    .create_application_command(|command| {
                        command.name("ping").description("A ping command")
                    })
                    .create_application_command(|command| {
                        command.name("exec").description("Execute a c++ snippet")
                            .create_option(|option| {
                                option.name("code")
                                    .description("Code to execute")
                                    .kind(ApplicationCommandOptionType::String)
                                    .required(true)
                            })
                            .create_option(|option| {
                                option.name("stdin")
                                    .description("Standard input to be redirected into the code")
                                    .kind(ApplicationCommandOptionType::String)
                                    .required(false)
                            })
                    })
            })
                .await;
        } else {
            commands = ApplicationCommand::get_global_application_commands(&ctx.http).await;
            println!("Commands were not updated")
        }
        println!("I now have the following global slash commands: {:#?}", commands);
    }

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        println!("INTERACTION RECEIVED");
        if let Interaction::ApplicationCommand(ref command) = interaction {
            // let author = command.member.expect("Command author");
            // let guild = ctx.cache().expect("Cache not present").guild(author.guild_id).await.expect("Guild not retrievable");


            let content = match command.data.name.as_str() {
                "ping" => {
                    "Pong!"
                }
                "exec" => {
                    let source_code = command.data.options
                        .get(0)
                        .expect("Expected required argument 'code'")
                        .value
                        .as_ref()
                        .expect("Expected non-empty argument 'code'")
                        .as_str()
                        .expect("Expecting string to be string");

                    let mut given_stdin = None;
                    if let Some(stdin) = command.data.options.get(1) {
                        given_stdin = Some(
                            Box::from(
                                stdin
                                    .value
                                    .as_ref()
                                    .expect("Expected non-empty given value for 'stdin'")
                                    .as_str()
                                    .expect("Str to str")
                            )
                        )
                    }


                    let data_read = ctx.data.read().await;
                    let sender = data_read.get::<CodeQueueSender>().expect("Code queue sender").clone();
                    /*let new_program = send_to_executor(
                        u64::from(interaction.id()),
                        Box::from(source_code),
                        given_stdin,
                        &sender
                    ).await;*/

                    let (one_sender, receiver) = tokio::sync::oneshot::channel::<CodeExecutionResult>();

                    let mut new_program = CodeToExecute {
                        id: u64::from(interaction.id()),
                        code: Box::from(source_code),
                        stdin: given_stdin,
                        oneshot_sender: one_sender
                    };

                    sender.send(new_program);

                    let result = receiver.await.expect("code execution result");

                    println!("{}{}{}", result.successful, result.stdout, result.stderr);

                    "Enqueued"
                }
                _ => "Command does not exist :("
            };

            if content != "" {
                command.create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| { message.content(content) })
                })
                    .await;
            };
        }
    }
}

async fn consume_queue(mut receiver: Receiver<CodeToExecute>) {
    loop {
        if let Some(program) = receiver.recv().await {
            executor::execute_code(program);
        }
        println!("Received code! Executing...")
    }
}


#[tokio::main]
async fn main() {
    // Configure the client with your Discord bot token in the environment.
    let token = "ODkzNzgyNTQ4ODY4NjU3MTUy.YVgd3Q.1PdUGIcOy4hRy2LaLIm6yfvG-nE";

    // The Application Id is usually the Bot User Id.
    let application_id: u64 = 893782548868657152;

    // Build our client.
    let mut client = Client::builder(token)
        .event_handler(Handler)
        .application_id(application_id)
        .await
        .expect("Error creating client");

    let (sender, receiver) = channel::<CodeToExecute>(5);

    {
        // Open the data lock in write mode, so keys can be inserted to it.
        let mut data = client.data.write().await;
        data.insert::<CodeQueueSender>(sender );
    }

    // Start a code consumer thread
    tokio::spawn(async move {
        consume_queue(receiver).await
    });

    // Finally, start a single shard, and start listening to events.
    //
    // Shards will automatically attempt to reconnect, and will perform
    // exponential backoff until it reconnects.
    if let Err(why) = client.start().await {
        println!("Client error: {:?}", why);
    }
}

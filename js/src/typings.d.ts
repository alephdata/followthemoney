import { IModelDatum } from './model'

declare module "defaultModel.json" {
    const value: IModelDatum;
    export default value;
}